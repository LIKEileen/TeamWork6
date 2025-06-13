from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..services.schedule_service import (
    get_user_schedule_list, add_single_schedule_event, 
    add_recurring_schedule_event, remove_schedule_event,
    import_excel_schedule, check_schedule_conflict
)
import logging
import os
import uuid

schedule_bp = Blueprint('schedule', __name__)

# 配置文件上传
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_request_data(data, required_fields):
    """验证请求数据"""
    if not data:
        return False, "请求数据不能为空"
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, "验证通过"

@schedule_bp.route('/user/schedule', methods=['POST'])
def get_user_schedule():
    """获取用户日程列表"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': []
            }), 400
        
        token = data.get('token')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        schedules, message = get_user_schedule_list(token, start_date, end_date)
        
        if schedules is not None:
            return jsonify({
                'code': 1,
                'message': message,
                'data': schedules
            })
        else:
            return jsonify({
                'code': 0,
                'message': message,
                'data': []
            }), 401
            
    except Exception as e:
        logging.error(f"Get user schedule error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': []
        }), 500

@schedule_bp.route('/user/schedule/add', methods=['POST'])
def add_schedule_event():
    """添加单个日程事件"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'title', 'date', 'start', 'end'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
        
        token = data.get('token')
        title = data.get('title')
        date = data.get('date')
        start = data.get('start')
        end = data.get('end')
        color = data.get('color', '#409EFF')
        force_create = data.get('forceCreate', False)  # 是否强制创建（忽略冲突）
        
        event, message = add_single_schedule_event(token, title, date, start, end, color, force_create)
        
        if event:
            return jsonify({
                'code': 1,
                'message': message,
                'data': event
            })
        else:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
            
    except Exception as e:
        logging.error(f"Add schedule event error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': {}
        }), 500

@schedule_bp.route('/user/schedule/add/recurring', methods=['POST'])
def add_recurring_event():
    """添加长期重复事件"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'title', 'start', 'end', 'frequency'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        title = data.get('title')
        start = data.get('start')
        end = data.get('end')
        frequency = data.get('frequency')
        custom_dates = data.get('customDates')
        color = data.get('color', '#409EFF')
        repeat_count = data.get('repeatCount')
        force_create = data.get('forceCreate', False)  # 是否强制创建（忽略冲突）
        
        success, message = add_recurring_schedule_event(token, title, start, end, frequency, custom_dates, color, repeat_count, force_create)
        
        if success:
            return jsonify({
                'code': 1,
                'message': message
            })
        else:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
            
    except Exception as e:
        logging.error(f"Add recurring event error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@schedule_bp.route('/user/schedule/delete', methods=['POST'])
def delete_schedule_event():
    """删除日程事件"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'eventId'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        event_id = data.get('eventId')
        
        success, message = remove_schedule_event(token, event_id)
        
        if success:
            return jsonify({
                'code': 1,
                'message': message
            })
        else:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
            
    except Exception as e:
        logging.error(f"Delete schedule event error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@schedule_bp.route('/user/schedule/import/excel', methods=['POST'])
def import_excel_schedule_route():
    """导入Excel课表"""
    try:
        # 验证token
        token = request.form.get('token')
        if not token:
            return jsonify({
                'code': 0,
                'message': 'token不能为空'
            }), 400
        
        # 检查文件
        if 'file' not in request.files:
            return jsonify({
                'code': 0,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'code': 0,
                'message': '没有选择文件'
            }), 400
        
        if file and allowed_file(file.filename):
            # 确保上传目录存在
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # 生成唯一文件名
            filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # 保存文件
            file.save(file_path)
            
            # 导入数据
            success, message = import_excel_schedule(token, file_path)
            
            if success:
                return jsonify({
                    'code': 1,
                    'message': message
                })
            else:
                return jsonify({
                    'code': 0,
                    'message': message
                }), 400
        else:
            return jsonify({
                'code': 0,
                'message': '不支持的文件格式，请上传.xlsx或.xls文件'
            }), 400
            
    except Exception as e:
        logging.error(f"Import excel schedule error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@schedule_bp.route('/user/schedule/import/school', methods=['POST'])
def import_school_schedule():
    """导入学校课表（暂未实现）"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'school'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        # TODO: 实现学校课表导入逻辑
        return jsonify({
            'code': 0,
            'message': '功能开发中，敬请期待'
        }), 501
        
    except Exception as e:
        logging.error(f"Import school schedule error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@schedule_bp.route('/user/schedule/check-conflict', methods=['POST'])
def check_conflict():
    """检查时间冲突"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'date', 'start', 'end'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {
                    'hasConflict': False,
                    'conflicts': []
                }
            }), 400
        
        token = data.get('token')
        date = data.get('date')
        start = data.get('start')
        end = data.get('end')
        exclude_event_id = data.get('excludeEventId')  # 编辑时排除当前事件
        
        conflicts, message = check_schedule_conflict(token, date, start, end, exclude_event_id)
        
        if conflicts is not None:
            return jsonify({
                'code': 1,
                'message': message,
                'data': {
                    'hasConflict': len(conflicts) > 0,
                    'conflicts': conflicts
                }
            })
        else:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {
                    'hasConflict': False,
                    'conflicts': []
                }
            }), 401
            
    except Exception as e:
        logging.error(f"Check conflict error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': {
                'hasConflict': False,
                'conflicts': []
            }
        }), 500