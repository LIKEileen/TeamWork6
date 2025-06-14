from ..models.user import get_user_by_phone_or_email, create_user, get_user_by_id, bind_phone, get_db_connection
from ..services.verification_service import verify_code
from passlib.hash import bcrypt
import jwt
import datetime
import traceback
from ..config import Config

def format_user_response(user, token):
    """格式化用户响应数据"""
    # 修复avatar逻辑，使用Config中的默认头像
    avatar = user.get('avatar')
    if not avatar or avatar == 'null' or avatar == '':
        avatar = Config.DEFAULT_AVATAR_URL
    
    return {
        'token': token,
        'nickname': user['nickname'],
        'avatar': avatar,
        'email': user['email'],
        'phone': user.get('phone'),  # 使用get方法防止KeyError
        'role': user.get('role', 'user')  # 提供默认值
    }

def is_token_blacklisted(token):
    """检查token是否在黑名单中"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id FROM token_blacklist WHERE token = ?', (token,))
        result = cursor.fetchone()
        is_blacklisted = result is not None
        
        if is_blacklisted:
            print(f"Token is blacklisted: {token[:20]}...")
        
        return is_blacklisted
        
    except Exception as e:
        print(f"Error checking token blacklist: {str(e)}")
        # 如果检查失败，为了安全起见，假设token有效
        return False
    finally:
        conn.close()

def logout_user(token):
    """用户退出登录（将token加入黑名单）"""
    try:
        if not token:
            return False, "token不能为空"
        
        print(f"Logging out user with token: {token[:20]}...")
        
        # 验证token是否有效
        payload = verify_token(token)
        if not payload:
            return False, "无效的token"
        
        # 将token添加到黑名单
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO token_blacklist (token, created_at)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (token,))
            
            conn.commit()
            print(f"Token added to blacklist successfully")
            
            # 清理过期的黑名单token（可选）
            cleanup_expired_tokens()
            
            return True, "退出成功"
            
        except Exception as db_error:
            print(f"Database error in logout: {str(db_error)}")
            return False, f"退出失败: {str(db_error)}"
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error in logout_user: {str(e)}")
        traceback.print_exc()
        return False, f"退出失败: {str(e)}"

def cleanup_expired_tokens():
    """清理过期的黑名单token"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除超过48小时的黑名单token
        expiry_time = datetime.datetime.now() - datetime.timedelta(hours=48)
        cursor.execute('''
            DELETE FROM token_blacklist 
            WHERE datetime(created_at) < datetime(?)
        ''', (expiry_time.isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} expired tokens from blacklist")
            
    except Exception as e:
        print(f"Error cleaning up expired tokens: {str(e)}")

def authenticate_user(phone=None, email=None, password=None):
    """用户登录验证"""
    try:
        print(f"Authenticating user - phone: {phone}, email: {email}")
        
        # 验证输入参数
        if not password:
            return None, "密码不能为空"
        
        if not (phone or email):
            return None, "请提供手机号或邮箱"
        
        # 获取用户
        user = get_user_by_phone_or_email(phone=phone, email=email)
        if not user:
            print("User not found")
            return None, "用户不存在"
        
        print(f"Found user: ID={user['id']}, nickname={user['nickname']}")
        
        # 验证密码
        if not bcrypt.verify(password, user['password_hash']):
            print("Password verification failed")
            return None, "密码错误"
        
        print("Password verified successfully")
        
        # 生成token
        token = generate_token(user)
        if not token:
            return None, "生成token失败"
        
        print(f"Login successful for user: {user['nickname']}")
        return format_user_response(user, token), "登录成功"
        
    except Exception as e:
        print(f"Error in authenticate_user: {str(e)}")
        traceback.print_exc()
        return None, f"登录失败: {str(e)}"

def register_user(phone, email, password, nickname):
    """用户注册"""
    try:
        print(f"Registering user - nickname: {nickname}, phone: {phone}, email: {email}")
        
        # 验证输入参数
        if not all([nickname, email, password]):
            return None, "昵称、邮箱和密码不能为空"
        
        if len(password) < 6:
            return None, "密码长度至少6位"
        
        # 验证邮箱格式
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return None, "邮箱格式不正确"
        
        # 验证手机号格式（如果提供）
        if phone:
            phone_pattern = r'^1[3-9]\d{9}$'
            if not re.match(phone_pattern, phone):
                return None, "手机号格式不正确"
        
        # 检查用户是否已存在
        existing_user = get_user_by_phone_or_email(phone=phone, email=email)
        if existing_user:
            if existing_user.get('phone') == phone:
                return None, "该手机号已被注册"
            if existing_user.get('email') == email:
                return None, "该邮箱已被注册"
        
        # 加密密码
        password_hash = bcrypt.hash(password)
        
        # 创建用户
        user_data = {
            'nickname': nickname,
            'phone': phone,
            'email': email,
            'password_hash': password_hash,
            'avatar': Config.DEFAULT_AVATAR_URL,
            'role': 'user'
        }
        
        user, message = create_user(user_data)
        if not user:
            return None, message
        
        print(f"User created successfully: ID={user['id']}, nickname={user['nickname']}")
        
        # 生成token
        token = generate_token(user)
        if not token:
            return None, "生成token失败"
        
        print(f"Registration successful for user: {user['nickname']}")
        return format_user_response(user, token), "注册成功"
        
    except Exception as e:
        print(f"Error in register_user: {str(e)}")
        traceback.print_exc()
        return None, f"注册失败: {str(e)}"

def verify_token(token):
    """验证JWT token"""
    try:
        if not token:
            print("Token is empty")
            return None
        
        print(f"Verifying token: {token[:30]}...")
        
        # 检查token是否在黑名单中
        if is_token_blacklisted(token):
            print("Token is blacklisted")
            return None
        
        # 解码token
        payload = jwt.decode(
            token, 
            Config.SECRET_KEY, 
            algorithms=['HS256']
        )
        
        print(f"Token decoded successfully: user_id={payload.get('user_id')}")
        
        # 检查token是否过期
        exp_timestamp = payload.get('exp')
        if not exp_timestamp:
            print("Token missing expiration time")
            return None
        
        if datetime.datetime.fromtimestamp(exp_timestamp) < datetime.datetime.utcnow():
            print("Token has expired")
            return None
        
        # 检查必要字段是否存在
        if 'user_id' not in payload:
            print("Token missing user_id")
            return None
        
        # 验证用户是否仍然存在
        user = get_user_by_id(payload['user_id'])
        if not user:
            print(f"User not found for user_id: {payload['user_id']}")
            return None
        
        # 确保payload包含完整的用户信息
        complete_payload = {
            'user_id': user['id'],
            'email': user['email'],
            'phone': user.get('phone'),
            'nickname': user['nickname'],
            'role': user.get('role', 'user'),
            'exp': payload.get('exp'),
            'iat': payload.get('iat')
        }
        
        print(f"Token verification successful for user: {user['nickname']}")
        return complete_payload
        
    except jwt.ExpiredSignatureError:
        print("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid JWT token: {str(e)}")
        return None
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        traceback.print_exc()
        return None

def generate_token(user):
    """生成JWT token"""
    try:
        print(f"Generating token for user: ID={user['id']}, nickname={user['nickname']}")
        
        # 确保用户数据完整
        if not user or not user.get('id') or not user.get('email'):
            print("User data incomplete for token generation")
            print(f"User data: {user}")
            return None
        
        # 构建token payload
        payload = {
            'user_id': user['id'],
            'email': user['email'],
            'phone': user.get('phone'),
            'nickname': user['nickname'],
            'role': user.get('role', 'user'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS),
            'iat': datetime.datetime.utcnow()
        }
        
        print(f"Token payload created: user_id={payload['user_id']}, email={payload['email']}")
        
        # 生成token
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        print(f"Token generated successfully: {token[:30]}...")
        
        return token
        
    except Exception as e:
        print(f"Error generating token: {str(e)}")
        traceback.print_exc()
        return None

def bind_user_phone(token, phone, verification_code):
    """绑定用户手机号（使用token和验证码验证）"""
    try:
        print(f"Starting bind_user_phone")
        print(f"Token: {token[:30] if token else 'None'}...")
        print(f"Phone: {phone}, Verification code: {verification_code}")
        
        # 验证必填字段
        if not token or not phone or not verification_code:
            return None, "token、手机号和验证码不能为空"
        
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或 token 无效"
        
        print(f"Token verified successfully for user: {payload['nickname']}")
        
        user_id = payload['user_id']
        email = payload.get('email')
        
        print(f"User ID: {user_id}, Email: {email}")
        
        # 验证邮箱验证码
        if not email:
            print("Email is missing from token payload")
            return None, "无法获取用户邮箱信息"
        
        print(f"Verifying code {verification_code} for email {email}")
        code_valid, code_message = verify_code(email, verification_code)
        if not code_valid:
            print(f"Code verification failed: {code_message}")
            return None, code_message
        
        print("Verification code is valid")
        
        # 验证手机号格式
        import re
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            return None, "手机号格式不正确"
        
        # 检查手机号是否已被其他用户使用
        existing_user = get_user_by_phone_or_email(phone=phone)
        if existing_user and existing_user['id'] != user_id:
            return None, "该手机号已被其他用户绑定"
        
        # 绑定手机号
        print(f"Binding phone {phone} to user {user_id}")
        updated_user, message = bind_phone(user_id, phone)
        if not updated_user:
            print(f"Phone binding failed: {message}")
            return None, message
        
        print(f"Phone bound successfully for user: {updated_user['nickname']}")
        
        # 生成新的token
        new_token = generate_token(updated_user)
        if not new_token:
            return None, "生成新token失败"
        
        print(f"New token generated after phone binding")
        return format_user_response(updated_user, new_token), "手机号绑定成功"
        
    except Exception as e:
        print(f"Error binding phone: {str(e)}")
        traceback.print_exc()
        return None, f"绑定手机号失败: {str(e)}"

def validate_user_input(data, required_fields):
    """验证用户输入数据"""
    missing_fields = []
    for field in required_fields:
        if not data.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, "验证通过"

def get_user_from_token(token):
    """从token获取用户信息"""
    try:
        payload = verify_token(token)
        if not payload:
            return None, "无效的token"
        
        user = get_user_by_id(payload['user_id'])
        if not user:
            return None, "用户不存在"
        
        return user, "获取用户信息成功"
        
    except Exception as e:
        print(f"Error getting user from token: {str(e)}")
        return None, f"获取用户信息失败: {str(e)}"