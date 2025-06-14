## 未完善 TODO

from flask import Blueprint, request, jsonify
from ..services.meeting_service import find_meeting_times, create_meeting, get_user_meetings
from ..services.auth_service import verify_token
from datetime import datetime, date
import logging

meeting_bp = Blueprint('meeting', __name__)

def validate_request_data(data, required_fields):
    """验证请求数据"""
    if not data:
        return False, "请求数据不能为空"
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, "验证通过"

@meeting_bp.route('/meeting/find-time', methods=['POST'])
def find_available_time():
    """查找可用的会议时间"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'participants', 'duration'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        participants = data.get('participants')
        duration = data.get('duration')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        # 验证token
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'code': 0,
                'message': '用户未登录或 token 无效'
            }), 401
        
        # 解析日期
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'code': 0,
                    'message': '开始日期格式不正确，应为 YYYY-MM-DD'
                }), 400
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'code': 0,
                    'message': '结束日期格式不正确，应为 YYYY-MM-DD'
                }), 400
        
        # 查找可用时间
        available_times, message = find_meeting_times(
            participants, duration, start_date, end_date
        )
        
        return jsonify({
            'code': 1,
            'message': message,
            'data': {
                'available_times': available_times
            }
        })
        
    except Exception as e:
        logging.error(f"Find meeting time error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@meeting_bp.route('/meeting/create', methods=['POST'])
def create_new_meeting():
    """创建新会议"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'title', 'start_time', 'end_time', 'participants'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        
        # 验证token
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'code': 0,
                'message': '用户未登录或 token 无效'
            }), 401
        
        user_id = payload['user_id']
        
        # 创建会议
        meeting, message = create_meeting(data, user_id)
        
        if meeting:
            return jsonify({
                'code': 1,
                'message': message,
                'data': meeting
            })
        else:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
    except Exception as e:
        logging.error(f"Create meeting error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@meeting_bp.route('/meeting/list', methods=['POST'])
def get_meeting_list():
    """获取用户的会议列表"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        # 验证token
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'code': 0,
                'message': '用户未登录或 token 无效'
            }), 401
        
        user_id = payload['user_id']
        
        # 解析日期
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'code': 0,
                    'message': '开始日期格式不正确，应为 YYYY-MM-DD'
                }), 400
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'code': 0,
                    'message': '结束日期格式不正确，应为 YYYY-MM-DD'
                }), 400
        
        # 获取会议列表
        meetings, message = get_user_meetings(user_id, start_date, end_date)
        
        return jsonify({
            'code': 1,
            'message': message,
            'data': {
                'meetings': meetings
            }
        })
        
    except Exception as e:
        logging.error(f"Get meeting list error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500