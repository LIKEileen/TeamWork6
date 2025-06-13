from flask import Blueprint, request, jsonify
from ..services.auth_service import authenticate_user, register_user, bind_user_phone, logout_user
from ..services.verification_service import send_verification_code, reset_user_password
from ..models.user import init_db
import logging

auth_bp = Blueprint('auth', __name__)

# 初始化数据库（应用启动时执行一次）
init_db()

def validate_request_data(data, required_fields):
    """验证请求数据"""
    if not data:
        return False, "请求数据不能为空"
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, "验证通过"

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        
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
        
        user_data, message = authenticate_user(phone=phone, email=email, password=password)
        
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
            }), 401
            
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': {}
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        data = request.get_json()
        print(f"Register request data: {data}")  # 调试日志
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['nickname', 'phone', 'email', 'password'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
        
        nickname = data.get('nickname')
        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')
        
        print(f"Processing registration for: nickname={nickname}, phone={phone}, email={email}")
        
        try:
            user_data, message = register_user(
                phone=phone.strip(), 
                email=email.strip(), 
                password=password, 
                nickname=nickname.strip()
            )
            
            print(f"Register service result: user_data={user_data}, message={message}")
            
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
                
        except Exception as register_error:
            print(f"Register service error: {str(register_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'code': 0,
                'message': f'注册处理失败: {str(register_error)}',
                'data': {}
            }), 500
            
    except Exception as e:
        print(f"Register route error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'code': 0,
            'message': f'服务器内部错误: {str(e)}',
            'data': {}
        }), 500

@auth_bp.route('/bind', methods=['POST'])
def bind_phone():
    """绑定手机号接口"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['nickname', 'password', 'phone'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': {}
            }), 400
        
        nickname = data.get('nickname')
        phone = data.get('phone')
        password = data.get('password')
        
        user_data, message = bind_user_phone(
            nickname=nickname, password=password, phone=phone
        )
        
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

@auth_bp.route('/send-verification-code', methods=['POST'])
def send_verification():
    """发送验证码接口"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['email'])
        if not valid:
            return jsonify({
                'code': 400,
                'message': message
            }), 400
        
        email = data.get('email')
        success, message = send_verification_code(email)
        
        if success:
            return jsonify({
                'code': 200,
                'message': message
            })
        else:
            return jsonify({
                'code': 400,
                'message': message
            }), 400
            
    except Exception as e:
        logging.error(f"Send verification code error: {str(e)}")
        return jsonify({
            'code': 400,
            'message': '服务器内部错误'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码接口"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['email', 'code', 'password'])
        if not valid:
            return jsonify({
                'code': 400,
                'message': message
            }), 400
        
        email = data.get('email')
        code = data.get('code')
        new_password = data.get('password')
        
        success, message = reset_user_password(email, code, new_password)
        
        if success:
            return jsonify({
                'code': 200,
                'message': message
            })
        else:
            return jsonify({
                'code': 400,
                'message': message
            }), 400
            
    except Exception as e:
        logging.error(f"Reset password error: {str(e)}")
        return jsonify({
            'code': 400,
            'message': '服务器内部错误'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """退出登录接口"""
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
        success, message = logout_user(token)
        
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
        logging.error(f"Logout error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 400