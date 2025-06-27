import json
import logging
from datetime import datetime

from flask import Blueprint, Response, jsonify, request
from openai import OpenAI

from ..models.user import get_user_by_email
from ..services.meeting_service import find_meeting_times, get_user_meetings

# Client initialization is now moved inside the request handler.

# --- Tool Definitions ---


# 1. Wrapper function for get_user_meetings to make it LLM-friendly (using email instead of user_id)
def get_meetings_by_email(
    user_email: str, start_date_str: str = None, end_date_str: str = None
):
    """
    Gets the meeting list for a user based on their email.
    """
    logging.info(f"Executing: get_meetings_by_email(user_email={user_email})")
    user = get_user_by_email(user_email)
    if not user:
        return {"error": f"User with email {user_email} not found."}

    user_id = user["id"]

    start_date = (
        datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
    )
    end_date = (
        datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
    )

    meetings, message = get_user_meetings(user_id, start_date, end_date)
    return {"meetings": meetings, "message": message}


# 2. A dictionary to map tool names from the LLM to your functions
available_tools = {
    "find_meeting_times": find_meeting_times,
    "get_meetings_by_email": get_meetings_by_email,
}

# 3. Tool schemas for the LLM to understand what it can call
tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "find_meeting_times",
            "description": "Find available meeting times for a group of participants.",
            "parameters": {
                "type": "object",
                "properties": {
                    "participants": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of participant email addresses.",
                    },
                    "key_participants": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of key participant email addresses. Their availability is prioritized.",
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "The desired duration of the meeting in minutes.",
                    },
                    "start_date_str": {
                        "type": "string",
                        "description": "The start date for the search, in 'YYYY-MM-DD' format. Defaults to today if not provided.",
                    },
                    "end_date_str": {
                        "type": "string",
                        "description": "The end date for the search, in 'YYYY-MM-DD' format. Defaults to 7 days from the start date if not provided.",
                    },
                },
                "required": ["participants", "duration_minutes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_meetings_by_email",
            "description": "Get the scheduled meetings for a specific user by their email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_email": {
                        "type": "string",
                        "description": "The email address of the user.",
                    },
                    "start_date_str": {
                        "type": "string",
                        "description": "The start date for the search, in 'YYYY-MM-DD' format. Defaults to no start date limit.",
                    },
                    "end_date_str": {
                        "type": "string",
                        "description": "The end date for the search, in 'YYYY-MM-DD' format. Defaults to no end date limit.",
                    },
                },
                "required": ["user_email"],
            },
        },
    },
]

# --- End of Tool Definitions ---


chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat_with_llm():
    """
    与AI日程助手（ScheduleBot）进行交互。

    该端点负责处理与大语言模型（LLM）的聊天交互。它支持函数调用（Tool Calling），
    能够理解并执行诸如查询会议、寻找空闲时间等任务。

    **认证方式**:
    - `Authorization`: 必须在请求头中提供 `Bearer Token` 进行认证。
    - `X-LLM-Base-URL`: 可选的请求头，用于指定LLM服务的基础URL。

    **调用示例 (cURL)**:
    ```bash
    curl -X POST http://127.0.0.1:5000/api/chat \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer sk-your-real-api-key" \
    -H "X-LLM-Base-URL: https://your-llm-provider.com/v1" \
    -d '{
      "model": "gpt-4",
      "messages": [
        {
          "role": "user",
          "content": "明天张教授有什么安排？"
        }
      ]
    }'
    ```

    ---
    tags:
      - Chat
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "Bearer Token for authentication. Format: Bearer <YOUR_API_KEY>"
      - name: X-LLM-Base-URL
        in: header
        type: string
        required: false
        description: "Optional. The base URL for the LLM service."
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - messages
            - model
          properties:
            messages:
              type: array
              description: "遵循OpenAI格式的消息列表，用于维持对话上下文。"
              items:
                type: object
                properties:
                  role:
                    type: string
                    enum: [system, user, assistant, tool]
                  content:
                    type: string
            model:
              type: string
              description: "指定要使用的大语言模型名称，例如 'gpt-4'。"
    responses:
      '200':
        description: "成功。返回包含LLM最终回复的JSON对象。"
        schema:
          type: object
          properties:
            response:
              type: string
              description: "LLM生成的最终文本回复。"
      '400':
        description: "请求无效。例如，缺少'messages'或'model'参数。"
        schema:
          type: object
          properties:
            error:
              type: string
      '401':
        description: "认证失败。请求头中缺少或包含无效的'Authorization'。"
        schema:
          type: object
          properties:
            error:
              type: string
      '500':
        description: "服务器内部错误。在与LLM交互或执行工具时发生意外。"
        schema:
          type: object
          properties:
            error:
              type: string
    """
    # --- Authentication Handling ---
    # 1. Authorization Header
    auth_header = request.headers.get("Authorization")
    # 验证Bearer格式
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Invalid authorization format"}), 401
    api_key = auth_header.split(" ")[1]

    base_url = request.headers.get("X-LLM-Base-URL")

    # 2. JSON Body
    data = request.get_json()
    if not data or "messages" not in data or "model" not in data:
        return jsonify({"error": "必须提供'messages'列表和'model'参数"}), 400

    messages = data["messages"]
    model_name = data["model"]

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        system_prompt_content = (
            '你是一款名为"ScheduleBot"的AI日程助手，专为企业内网设计。'
            "你的职责是利用现有工具高效处理并回复员工关于会议、日历和日程的查询。"
            "始终提供可操作的帮助，避免声明无法访问数据。"
            f'当前服务器时间是 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}，请根据此时间来理解所有相对时间，例如"明天"。'
        )
        system_prompt = {"role": "system", "content": system_prompt_content}

        if not messages or messages[0].get("role") != "system":
            messages.insert(0, system_prompt)

        # --- First Call to check for tool calls ---
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools_definition,
            tool_choice="auto",
        )

        if not response.choices:
            logging.error(
                "LLM API returned empty choices on first call. Full response: %s",
                response.model_dump_json(),
            )
            return jsonify({"error": "LLM API returned an unexpected response."}), 500

        response_message = response.choices[0].message
        messages.append(response_message)
        tool_calls = response_message.tool_calls

        # --- Path 1: Tool call is requested ---
        if tool_calls:
            logging.info(f"Tool calls requested: {tool_calls}")
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools.get(function_name)
                if not function_to_call:
                    tool_result = f"Error: Tool '{function_name}' not found."
                else:
                    function_args = json.loads(tool_call.function.arguments)
                    try:
                        function_response = function_to_call(**function_args)
                        tool_result = json.dumps(function_response, ensure_ascii=False)
                    except Exception as e:
                        tool_result = f"Error executing tool '{function_name}': {e}"

                logging.info(f"Tool result for {function_name}: {tool_result}")
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": tool_result,
                    }
                )

            # --- Second Call: Get final answer ---
            logging.info("Making second call to LLM for final answer.")
            second_response = client.chat.completions.create(
                model=model_name,
                messages=messages,
            )

            if not second_response.choices:
                logging.error(
                    "LLM API returned empty choices on second call. Full response: %s",
                    second_response.model_dump_json(),
                )
                return jsonify({"error": "LLM API returned an unexpected response."}), 500

            final_message = second_response.choices[0].message.content
            return jsonify({"response": final_message})

        # --- Path 2: No tool call, LLM answered directly ---
        else:
            final_message = response_message.content
            logging.info(f"Direct response from LLM: {final_message}")
            if final_message:
                return jsonify({"response": final_message})
            else:
                # Handle cases where the response might be empty
                return jsonify({"response": ""})

    except Exception as e:
        logging.error(f"An error occurred during chat generation: {e}", exc_info=True)
        error_message = f"An unexpected error occurred: {str(e)}"
        return jsonify({"error": error_message}), 500
