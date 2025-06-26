# Author: 唐震
import logging
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..models.meeting import create_meeting_in_db, get_meetings_by_user_id
from ..models.user import get_user_by_email
from ..models.schedule import get_user_schedules
from .util import DAY_NAMES, merge_intervals, subtract_intervals


def _get_remaining_work_time(
    start_date: datetime.date,
    end_date: datetime.date,
    workdays: Optional[List[str]] = None,
    start_hour: int = 9,
    end_hour: int = 17,
) -> Dict[str, List[Tuple[int, int]]]:
    """计算从今天起，在指定日期范围内，每个工作日剩余的工作时间。

    Args:
        start_date (datetime.date): 开始日期。
        end_date (datetime.date): 结束日期。
        workdays (Optional[List[str]]): 工作日列表，例如 ['Monday', 'Tuesday']。默认为周一到周五。
        start_hour (int): 工作日开始小时。默认为 9。
        end_hour (int): 工作日结束小时。默认为 17。

    Returns:
        Dict[str, List[Tuple[int, int]]]: 一个字典，键是日期字符串，值是剩余工作时间的分钟元组列表。
    """
    if workdays is None:
        workdays = DAY_NAMES[:-2]  # 默认周一到周五

    now = datetime.now()
    result = {}
    current_date = start_date
    while current_date <= end_date:
        day_name = DAY_NAMES[current_date.weekday()]
        if day_name not in workdays:
            current_date += timedelta(days=1)
            continue

        day_start_minute = start_hour * 60
        day_end_minute = end_hour * 60

        if current_date == now.date():
            # 处理今天：从当前时间或工作开始时间（取较晚者）到工作结束时间
            current_minutes = now.hour * 60 + now.minute
            interval_start = max(current_minutes, day_start_minute)
            if interval_start < day_end_minute:
                result[str(current_date)] = [(interval_start, day_end_minute)]
        elif current_date > now.date():
            # 处理未来的日期：完整的工作时间段
            result[str(current_date)] = [(day_start_minute, day_end_minute)]

        current_date += timedelta(days=1)
    return result


def _get_free_time(
    remain_time: Dict[str, List[Tuple[int, int]]],
    busy_time: Dict[str, List[Tuple[int, int]]],
) -> Dict[str, List[Tuple[int, int]]]:
    """从剩余时间中减去忙碌时间，计算空闲时间。

    Args:
        remain_time (Dict[str, List[Tuple[int, int]]]): 剩余时间段。
        busy_time (Dict[str, List[Tuple[int, int]]]): 忙碌时间段。

    Returns:
        Dict[str, List[Tuple[int, int]]]: 计算出的空闲时间段。
    """
    free_time = {}
    for key, value in remain_time.items():
        busy_intervals = busy_time.get(key, [])
        free_time[key] = subtract_intervals(value, busy_intervals)
    return free_time


def _recursive_find(free_time_slots: List[Dict], duration: int) -> List[int]:
    """根据参与者的空闲时间和重要性，递归地寻找所有人都可用的会议开始时间。

    函数首先满足最重要参与者的时间，然后逐步扩展到所有参与者。

    Args:
        free_time_slots (List[Dict]): 参与者的空闲时间信息列表。每个字典包含:
            - 'id': 参与者ID
            - 'important': 重要性级别
            - 'free_time': 空闲时间段列表 (start_minute, end_minute)
        duration (int): 会议持续时间（分钟）。

    Returns:
        List[int]: 所有参与者都可用的会议开始时间的分钟列表。
    """
    # 为一天中的每一分钟（可作为开始时间）创建一个布尔标记列表
    available_begin = [True] * (60 * 24 + 1 - duration)
    # 按重要性级别降序排序，优先满足重要人物
    importance_levels = sorted({p["important"] for p in free_time_slots}, reverse=True)
    # 初始可用时间为全天所有可能的开始分钟数
    available_begin_id = list(range(len(available_begin)))

    # 从最重要的人开始，层层筛选，不断缩小可用时间范围
    for importance_level in importance_levels:
        # 获取当前及更高重要性级别的所有参与者
        level_participants = [
            p for p in free_time_slots if p["important"] >= importance_level
        ]
        num_participants = len(level_participants)
        if num_participants == 0:
            continue

        # 临时存储当前级别筛选后的可用时间
        temp_available_begin = [False] * len(available_begin)
        # 仅在上一轮筛选出的可用时间点中查找
        for i in available_begin_id:
            count = 0
            # 检查当前时间点是否对本级别所有人都可用
            for slot in level_participants:
                for start, end in slot["free_time"]:
                    if start <= i and (i + duration) <= end:
                        count += 1
                        break  # 该参与者有空，跳出内层循环继续检查下一个人

            # 如果本级别所有人都空闲，则标记该时间点可用
            if count == num_participants:
                temp_available_begin[i] = True

        # 更新可用时间ID列表
        new_available_begin_id = [i for i, v in enumerate(temp_available_begin) if v]

        # 如果没有找到共同时间，则无法满足当前重要性级别，使用上一轮的结果
        if not new_available_begin_id:
            break

        # 否则，用当前结果更新可用时间，用于下一轮（更低重要性）的筛选
        available_begin_id = new_available_begin_id

    return available_begin_id


def find_meeting_times(
    participants: List[str],
    key_participants: List[str],
    duration_minutes: int,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
) -> Tuple[Dict[str, List[Dict[str, str]]], str]:
    """寻找多个参与者共同的会议时间。

    Args:
        participants (List[str]): 参与者邮箱列表。
        key_participants (List[str]): 关键参与者邮箱列表。
        duration_minutes (int): 会议持续时间（分钟）。
        start_date_str (Optional[str]): 搜索开始日期。默认为今天。
        end_date_str (Optional[str]): 搜索结束日期。默认为7天后。

    Returns:
        Tuple[Dict[str, List[Dict[str, str]]], str]: 一个元组，第一个元素是可用会议时间的字典，
                                                      键是日期，值是时间段列表。第二个元素是消息。
    """
    try:
        logging.info(f"Finding meeting times for participants: {participants}")
        logging.info(f"Duration: {duration_minutes} minutes")

        # 1. 解析日期，如果未提供，则设置默认范围
        start_date = (
            datetime.fromisoformat(start_date_str).date()
            if start_date_str
            else datetime.now().date()
        )
        end_date = (
            datetime.fromisoformat(end_date_str).date()
            if end_date_str
            else start_date + timedelta(days=7)
        )

        # 2. 获取用户信息
        user_map: Dict[str, Optional[Dict]] = {
            user_email: get_user_by_email(user_email) for user_email in participants
        }
        for email, user in user_map.items():
            if not user:
                return {}, f"参与者 {email} 未找到"

        # 3. 获取所有人的日程并转换为分钟为单位的忙碌时间区间
        person_busy_time_list = []
        for email, user in user_map.items():
            # 从数据库获取会议列表
            meetings: List[Dict[str, Any]] = get_meetings_by_user_id(
                user["id"], start_date, end_date
            )
            # 从数据库获取个人日程列表
            schedules: List[Dict[str, Any]] = get_user_schedules(
                user["id"], start_date, end_date
            )

            busy_time: dict[str, List[int]] = {}

            # 合并会议和个人日程
            all_events = meetings + schedules
            for event in all_events:
                # 转换时间为UTC时区并提取分钟数
                if "start_time" in event:  # 会议
                    start = datetime.fromisoformat(
                        event["start_time"].replace("Z", "+00:00")
                    )
                    end = datetime.fromisoformat(
                        event["end_time"].replace("Z", "+00:00")
                    )
                    date_str = str(start.date())
                    if date_str not in busy_time:
                        busy_time[date_str] = []
                    busy_time[date_str].append(
                        (start.hour * 60 + start.minute, end.hour * 60 + end.minute)
                    )
                elif "date" in event:  # 个人日程
                    event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
                    if start_date <= event_date <= end_date:
                        date_str = str(event_date)
                        if date_str not in busy_time:
                            busy_time[date_str] = []
                        start_minute = int(event["start"].split(":")[0]) * 60 + int(
                            event["start"].split(":")[1]
                        )
                        end_minute = int(event["end"].split(":")[0]) * 60 + int(
                            event["end"].split(":")[1]
                        )
                        busy_time[date_str].append((start_minute, end_minute))

            for date_str in busy_time:
                # 合并同一天的忙碌时间，减少区间数量
                busy_time[date_str] = merge_intervals(busy_time[date_str])

            person_busy_time_list.append(
                {
                    "id": user["id"],
                    "important": 1
                    if email in key_participants
                    else 0,  # 标记关键参与者
                    "busy_time": busy_time,
                }
            )

        logging.info(f"person_busy_time_list:{person_busy_time_list}")

        # 4. 计算每天每个人的空闲时间
        remain_time = _get_remaining_work_time(start_date, end_date)
        everyday_free_time_list = {}
        for d_str in remain_time.keys():
            everyday_free_time_list[d_str] = []
            for person in person_busy_time_list:
                # 从工作时间中减去忙碌时间得到空闲时间
                person_daily_free = _get_free_time(
                    {d_str: remain_time[d_str]}, person["busy_time"]
                )
                everyday_free_time_list[d_str].append(
                    {
                        "id": person["id"],
                        "important": person["important"],
                        "free_time": person_daily_free.get(d_str, []),
                    }
                )

        # 5. 找出每天所有参与者都可用的会议时间
        available_meeting_times = {}
        for day_str, free_slots in everyday_free_time_list.items():
            # 使用递归查找算法找出共同的开始时间点
            start_minutes = _recursive_find(free_slots, duration_minutes)

            # 如果没有找到任何可用的时间点，则跳过当天
            if not start_minutes:
                continue

            day_date = datetime.fromisoformat(day_str).date()
            times = []
            for minute in start_minutes:
                # 将分钟转换为datetime对象
                start_time = datetime.combine(
                    day_date, time(hour=minute // 60, minute=minute % 60)
                )
                end_time = start_time + timedelta(minutes=duration_minutes)
                times.append(
                    {
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                    }
                )
            available_meeting_times[day_str] = times

        logging.info(f"Found {len(available_meeting_times)} suitable days")
        return available_meeting_times, "查找成功"

    except Exception as e:
        logging.error(f"Error finding meeting times: {str(e)}")
        return {}, f"查找会议时间失败: {str(e)}"


def create_meeting(
    meeting_data: Dict[str, Any], creator_id: int
) -> Tuple[Optional[Dict[str, Any]], str]:
    """创建会议。

    Args:
        meeting_data (Dict[str, Any]): 会议数据，包含 title, start_time, end_time, participants 等。
        creator_id (int): 创建者的用户ID。

    Returns:
        Tuple[Optional[Dict[str, Any]], str]: 一个元组，第一个元素是创建的会议对象（如果成功），第二个元素是消息。
    """
    try:
        logging.info(f"Creating meeting: {meeting_data}")

        # 验证必填字段
        required_fields = ["title", "start_time", "end_time", "participants"]
        for field in required_fields:
            if not meeting_data.get(field):
                return None, f"{field} 不能为空"

        # 验证时间格式，并将其从ISO格式（带'Z'）转换成datetime对象
        try:
            start_time = datetime.fromisoformat(
                meeting_data["start_time"].replace("Z", "+00:00")
            )
            end_time = datetime.fromisoformat(
                meeting_data["end_time"].replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            return None, "时间格式不正确"

        if start_time >= end_time:
            return None, "开始时间必须早于结束时间"

        # 解析参与者
        participant_emails: List[str] = meeting_data.get("participants", [])
        key_participant_emails: List[str] = meeting_data.get("key_participants", [])

        # 关键成员必须是参会成员的子集
        if not set(key_participant_emails).issubset(set(participant_emails)):
            return None, "关键成员必须是参会成员的一部分"

        participant_ids = []
        unresolved_emails = []
        for email in participant_emails:
            # 通过邮箱查找用户，获取其ID
            user = get_user_by_email(email)
            if user:
                participant_ids.append(user["id"])
            else:
                unresolved_emails.append(email)

        if unresolved_emails:
            return None, f"以下普通参与者未找到: {', '.join(unresolved_emails)}"

        key_participant_ids = []
        unresolved_key_emails = []
        for email in key_participant_emails:
            user: Optional[Dict] = get_user_by_email(email)
            if user:
                key_participant_ids.append(user["id"])
            else:
                unresolved_key_emails.append(email)

        if unresolved_key_emails:
            return None, f"以下关键参与者未找到: {', '.join(unresolved_key_emails)}"

        # 保存到数据库
        meeting, message = create_meeting_in_db(
            meeting_data, creator_id, participant_ids, key_participant_ids
        )

        if meeting:
            logging.info(f"Meeting created successfully: {meeting['id']}")

        return meeting, message

    except Exception as e:
        logging.error(f"Error creating meeting: {str(e)}")
        return None, f"创建会议失败: {str(e)}"


def get_user_meetings(
    user_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """获取用户的会议列表。

    Args:
        user_id (int): 用户的ID。
        start_date (Optional[datetime.date]): 开始日期，用于过滤会议。默认为None。
        end_date (Optional[datetime.date]): 结束日期，用于过滤会议。默认为None。

    Returns:
        Tuple[List[Dict[str, Any]], str]: 一个元组，第一个元素是会议列表，第二个元素是消息。
    """
    try:
        logging.info(f"Getting meetings for user: {user_id}")

        # 从数据库查询用户的会议
        meetings = get_meetings_by_user_id(user_id, start_date, end_date)

        logging.info(f"Found {len(meetings)} meetings for user")
        return meetings, "获取成功"

    except Exception as e:
        logging.error(f"Error getting user meetings: {str(e)}")
        return [], f"获取会议列表失败: {str(e)}"
