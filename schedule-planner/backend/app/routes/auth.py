from flask import Blueprint, request, jsonify
from ..services.auth_service import authenticate_user, register_user, bind_user_phone, logout_user
from ..services.verification_service import send_verification_code, reset_user_password
from ..models.user import init_db
import logging

auth_bp = Blueprint('auth', __name__)

def validate_request_data(data, required_fields):
    """验证请求数据"""
    if not data:
        return False, "请求数据不能为空"
    
    missing_fields = []
    for field in required_fields:
        if not data.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, "验证通过"

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        data = request.get_json()
        logging.info(f"Register request: {data}")
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['nickname', 'email', 'password'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
        
        nickname = data.get('nickname')
        phone = data.get('phone')  # 可选
        email = data.get('email')
        password = data.get('password')
        
        # 构建用户数据
        user_data = {
            'nickname': nickname,
            'email': email,
            'password': password
        }
        
        # 如果提供了手机号，添加到用户数据中
        if phone:
            user_data['phone'] = phone
        
        # 注册用户 - 修复函数调用
        user_info, message = register_user(user_data)
        
        if user_info:
            return jsonify({
                'code': 1,
                'message': 'success',
                'data': user_info
            })
        else:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
            
    except Exception as e:
        logging.error(f"Register error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'code': 0,
            'message': f'服务器内部错误: {str(e)}',
            'data': {}
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        logging.info(f"Login request: {data}")
        
        # 验证必填字段
        if not data or not data.get('password'):
            return jsonify({
                'code': 0,
                'message': '密码不能为空',
                'data': {}
            }), 400
        
        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')
        
        if not (phone or email):
            return jsonify({
                'code': 0,
                'message': '请提供手机号或邮箱',
                'data': {}
            }), 400
        
        # 确定登录标识符
        login_identifier = email if email else phone
        
        # 用户登录 - 修复函数调用
        user, message = authenticate_user(login_identifier, password)
        
        if user:
            # 生成token
            from ..services.auth_service import generate_token, format_user_response
            token = generate_token(user)
            if not token:
                return jsonify({
                    'code': 0,
                    'message': '生成token失败',
                    'data': {}
                }), 500
            
            user_data = format_user_response(user, token)
            return jsonify({
                'code': 1,
                'message': 'success',
                'data': user_data
            })
        else:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
            
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'code': 0,
            'message': f'服务器内部错误: {str(e)}',
            'data': {}
        }), 500

@auth_bp.route('/send-verification-code', methods=['POST'])
def send_verification():
    """发送验证码接口（修复函数名）"""
    try:
        data = request.get_json()
        logging.info(f"Send verification code request: {data}")
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['email'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
        
        email = data.get('email')
        code_type = data.get('type', 'bind_phone')  # 默认为绑定手机号
        
        # 验证邮箱格式
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'code': 0,
                'message': '邮箱格式不正确',
                'data': {}
            }), 400
        
        # 发送验证码
        success, message = send_verification_code(email, code_type)
        
        if success:
            return jsonify({
                'code': 1,
                'message': message,
                'data': {}
            })
        else:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
            
    except Exception as e:
        logging.error(f"Send verification code error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': {}
        }), 500

@auth_bp.route('/bind', methods=['POST'])
def bind():
    """绑定手机号接口"""
    try:
        data = request.get_json()
        logging.info(f"Bind phone request: {data}")
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'phone', 'verification_code'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
        
        token = data.get('token')
        phone = data.get('phone')
        verification_code = data.get('verification_code')
        
        # 绑定手机号
        user_data, message = bind_user_phone(token, phone, verification_code)
        
        if user_data:
            return jsonify({
                'code': 1,
                'message': message,
                'data': user_data
            })
        else:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
            
    except Exception as e:
        logging.error(f"Bind phone error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': {}
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码接口"""
    try:
        data = request.get_json()
        logging.info(f"Reset password request: {data}")
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['email', 'code', 'password'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
        
        email = data.get('email')
        code = data.get('code')
        new_password = data.get('password')
        
        # 重置密码
        success, message = reset_user_password(email, code, new_password)
        
        if success:
            return jsonify({
                'code': 1,
                'message': message,
                'data': {}
            })
        else:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
            
    except Exception as e:
        logging.error(f"Reset password error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': {}
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户退出登录接口"""
    try:
        data = request.get_json()
        logging.info(f"Logout request: {data}")
        
        # 验证必填字段
        if not data or not data.get('token'):
            return jsonify({
                'code': 0,
                'message': 'token不能为空',
                'data': {}
            }), 400
        
        token = data.get('token')
        
        # 退出登录
        success, message = logout_user(token)
        
        if success:
            return jsonify({
                'code': 1,
                'message': message,
                'data': {}
            })
        else:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
            
    except Exception as e:
        logging.error(f"Logout error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': {}
        }), 500