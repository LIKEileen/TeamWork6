import jwt
import datetime
from ..models.user import (
    get_user_by_phone_or_email, verify_password, create_user, 
    get_user_by_nickname, bind_phone, add_token_to_blacklist, 
    is_token_blacklisted
)
from ..config import Config

def generate_token(user):
    """生成JWT token"""
    payload = {
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        'iat': datetime.datetime.utcnow(),
        'role': user['role']
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def format_user_response(user, token):
    """格式化用户响应数据"""
    return {
        'token': token,
        'nickname': user['nickname'],
        'avatar': user['avatar'] or 'https://imgheybox.max-c.com/bbs/2024/09/19/1dc7d8a7978e8e9be26498747ef493ce/thumb.png',
        'email': user['email'],
        'phone': user['phone'],
        'role': user['role']
    }

def authenticate_user(phone=None, email=None, password=None):
    """验证用户身份并生成token"""
    from ..models.user import get_user_by_phone_or_email, verify_password
    
    try:
        print(f"Authenticating user - phone: {phone}, email: {email}")  # 调试日志
        
        # 获取用户信息
        user = get_user_by_phone_or_email(phone, email)
        print(f"Found user: {user}")  # 调试日志
        
        if not user:
            print("User not found")  # 调试日志
            return None, "用户不存在"
        
        # 验证密码
        print(f"Verifying password for user ID: {user['id']}")  # 调试日志
        print(f"Stored password hash: {user.get('password_hash', 'NOT_FOUND')}")  # 调试日志
        
        if verify_password(password, user['password_hash']):
            print("Password verification successful")  # 调试日志
            
            # 生成token
            token = generate_token(user)
            
            # 格式化响应
            response_data = format_user_response(user, token)
            print(f"Login successful, response: {response_data}")  # 调试日志
            
            return response_data, "登录成功"
        else:
            print("Password verification failed")  # 调试日志
            return None, "密码错误"
            
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, f"登录失败: {str(e)}"

def register_user(phone, email, password, nickname):
    """注册新用户"""
    try:
        # 验证必填字段
        if not all([phone, email, password, nickname]):
            return None, "所有字段都不能为空"
        
        # 去除空格
        phone = phone.strip()
        email = email.strip()
        nickname = nickname.strip()
        
        # 验证字段不为空
        if not all([phone, email, nickname]):
            return None, "所有字段都不能为空"
        
        # 验证手机号格式
        import re
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            return None, "手机号格式不正确"
        
        # 验证邮箱格式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return None, "邮箱格式不正确"
        
        # 验证密码长度
        if len(password) < 6 or len(password) > 100:
            return None, "密码长度必须在6-100位之间"
        
        # 验证昵称长度
        if len(nickname) > 50:
            return None, "昵称长度不能超过50个字符"
        
        # 创建用户
        user, message = create_user(nickname, phone, email, password)
        
        if user:
            print(f"User data from create_user: {user}")  # 调试日志
            
            # 确保user中有id字段
            if 'id' not in user:
                print(f"Error: user dict missing 'id' field. User data: {user}")
                return None, "用户创建失败：缺少用户ID"
            
            try:
                # 生成token
                token = generate_token(user)  # 直接传入完整的user对象
                print(f"Generated token: {token}")  # 调试日志
                
                return {
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'nickname': user['nickname'],
                        'phone': user['phone'],
                        'email': user['email'],
                        'avatar': user['avatar'],  # 包含默认头像
                        'role': user.get('role', 'user')
                    }
                }, message
                
            except Exception as token_error:
                print(f"Token generation error: {str(token_error)}")
                import traceback
                traceback.print_exc()
                return None, f"Token生成失败: {str(token_error)}"
        else:
            return None, message
            
    except Exception as e:
        print(f"Register user error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, f"注册失败: {str(e)}"

def bind_user_phone(nickname=None, password=None, phone=None):
    """绑定用户手机号并生成新token"""
    if not nickname or not password or not phone:
        return None, "昵称、密码和手机号不能为空"
    
    user = get_user_by_nickname(nickname)
    if not user:
        return None, "用户不存在"
    
    if not verify_password(user['password'], password):
        return None, "密码错误"
    
    updated_user, message = bind_phone(user['id'], phone)
    if not updated_user:
        return None, message
    
    token = generate_token(updated_user)
    return format_user_response(updated_user, token), message

def logout_user(token):
    """退出登录，验证token并加入黑名单"""
    if not token:
        return None, "Token不能为空"
    
    if is_token_blacklisted(token):
        return None, "Token已失效"
    
    try:
        jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None, "Token已过期"
    except jwt.InvalidTokenError:
        return None, "无效的Token"
    
    add_token_to_blacklist(token)
    return True, "退出成功"

def verify_token(token):
    """验证token有效性"""
    if not token or is_token_blacklisted(token):
        return None
    
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None