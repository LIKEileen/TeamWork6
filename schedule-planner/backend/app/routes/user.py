from flask import Blueprint, request, jsonify
from ..services.user_service import update_user_profile, change_password, upload_avatar, get_user_profile
import logging

user_bp = Blueprint('user', __name__)

def validate_request_data(data, required_fields):
    """验证请求数据"""
    if not data:
        return False, "请求数据不能为空"
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, "验证通过"

@user_bp.route('/user/update', methods=['POST'])
def update_user():
    """更新用户信息"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'nickname'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        nickname = data.get('nickname')
        phone = data.get('phone')
        email = data.get('email')
        
        user_info, message = update_user_profile(token, nickname, phone, email)
        
        if user_info:
            return jsonify({
                'code': 1,
                'message': "用户信息已更新",
                'data': user_info
            })
        else:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
            
    except Exception as e:
        logging.error(f"Update user error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@user_bp.route('/user/change-password', methods=['POST'])
def change_user_password():
    """修改密码"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'oldPassword', 'newPassword'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')
        
        success, message = change_password(token, old_password, new_password)
        
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
        logging.error(f"Change password error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@user_bp.route('/user/avatar/upload', methods=['POST'])
def upload_user_avatar():
    """上传头像"""
    try:
        # 获取token
        token = request.form.get('token')
        if not token:
            return jsonify({
                'code': 0,
                'message': 'token不能为空'
            }), 400
        
        # 检查文件
        if 'avatar' not in request.files:
            return jsonify({
                'code': 0,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['avatar']
        
        avatar_url, message = upload_avatar(token, file)
        
        if avatar_url:
            return jsonify({
                'code': 1,
                'message': message,
                'avatarUrl': avatar_url
            })
        else:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
            
    except Exception as e:
        logging.error(f"Upload avatar error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@user_bp.route('/user/profile', methods=['POST'])
def get_user_info():
    """获取用户资料"""
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
        
        user_info, message = get_user_profile(token)
        
        if user_info:
            return jsonify({
                'code': 1,
                'message': message,
                'data': user_info
            })
        else:
            return jsonify({
                'code': 0,
                'message': message
            }), 401
            
    except Exception as e:
        logging.error(f"Get user profile error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500