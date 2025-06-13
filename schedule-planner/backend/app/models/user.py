import sqlite3
from passlib.hash import bcrypt
import datetime
import os
from ..config import Config

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 支持字典式访问
    return conn

def init_db():
    """初始化用户数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建完整的用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            phone TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            avatar TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建验证码表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        )
    ''')
    
    # 创建token黑名单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS token_blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verification_email ON verification_codes(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_token_blacklist ON token_blacklist(token)')
    
    conn.commit()
    conn.close()
    print("User database initialized successfully")

def get_user_by_phone_or_email(phone, email):
    """通过手机号或邮箱获取用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if phone:
            print(f"Searching user by phone: {phone}")  # 调试日志
            cursor.execute('''
                SELECT id, nickname, phone, email, password_hash, avatar, role, created_at, updated_at
                FROM users WHERE phone = ?
            ''', (phone,))
        elif email:
            print(f"Searching user by email: {email}")  # 调试日志
            cursor.execute('''
                SELECT id, nickname, phone, email, password_hash, avatar, role, created_at, updated_at
                FROM users WHERE email = ?
            ''', (email,))
        else:
            return None
        
        user = cursor.fetchone()
        print(f"Database query result: {dict(user) if user else None}")  # 调试日志
        
        return dict(user) if user else None
        
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None
    finally:
        conn.close()

def get_user_by_nickname(nickname):
    """根据昵称查询用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE nickname = ?', (nickname,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

def create_user(nickname, phone, email, password, role='user'):
    """创建新用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查手机号是否已存在
        if phone:
            cursor.execute('SELECT id FROM users WHERE phone = ?', (phone,))
            if cursor.fetchone():
                return None, "手机号已被注册"
        
        # 检查邮箱是否已存在
        if email:
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return None, "邮箱已被注册"
        
        # 加密密码
        password_hash = hash_password(password)
        
        # 设置默认头像
        default_avatar = Config.DEFAULT_AVATAR_URL
        
        # 插入新用户 - 包含默认头像
        cursor.execute('''
            INSERT INTO users (nickname, phone, email, password_hash, avatar, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (nickname, phone, email, password_hash, default_avatar, role))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # 确保获取完整的用户信息，包括id字段
        cursor.execute('''
            SELECT id, nickname, phone, email, avatar, role, created_at, updated_at
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        
        if user:
            # 确保返回的是字典格式，包含所有字段
            user_dict = {
                'id': user['id'],
                'nickname': user['nickname'],
                'phone': user['phone'],
                'email': user['email'],
                'avatar': user['avatar'],
                'role': user['role'],
                'created_at': user['created_at'],
                'updated_at': user['updated_at']
            }
            print(f"Created user dict: {user_dict}")  # 调试日志
            return user_dict, "用户创建成功"
        else:
            return None, "用户创建失败"
        
    except sqlite3.IntegrityError as e:
        print(f"IntegrityError: {str(e)}")
        return None, f"数据完整性错误: {str(e)}"
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印完整错误堆栈
        return None, f"创建用户失败: {str(e)}"
    finally:
        conn.close()

def bind_phone(user_id, phone):
    """绑定手机号到用户账户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查手机号是否已被其他用户使用
        existing_user = get_user_by_phone_or_email(phone=phone)
        if existing_user and existing_user['id'] != user_id:
            return None, "手机号已被其他用户绑定"
        
        # 更新手机号
        cursor.execute('''
            UPDATE users 
            SET phone = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (phone, user_id))
        
        # 获取更新后的用户
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.commit()
        return dict(user) if user else None, "绑定成功"
        
    except sqlite3.IntegrityError:
        return None, "手机号已存在"
    except Exception as e:
        return None, f"绑定失败: {str(e)}"
    finally:
        conn.close()

def verify_user_login(phone=None, email=None, password=None):
    """验证用户登录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if phone:
            cursor.execute('SELECT id, nickname, password_hash, role FROM users WHERE phone = ?', (phone,))
        elif email:
            cursor.execute('SELECT id, nickname, password_hash, role FROM users WHERE email = ?', (email,))
        else:
            return None, "手机号或邮箱不能为空"
        
        user = cursor.fetchone()
        
        if not user:
            return None, "用户不存在"
        
        # 验证密码 - 使用 password_hash 字段
        if verify_password(password, user['password_hash']):
            return {
                'user_id': user['id'],
                'nickname': user['nickname'],
                'role': user['role']
            }, "登录成功"
        else:
            return None, "密码错误"
            
    except Exception as e:
        print(f"Login verification error: {str(e)}")
        return None, f"登录验证失败: {str(e)}"
    finally:
        conn.close()

def reset_password(email, new_password):
    """重置密码"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 加密新密码
        password_hash = bcrypt.hash(new_password)
        
        # 更新密码 - 使用 password_hash 字段
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE email = ?
        ''', (password_hash, email))
        
        if cursor.rowcount > 0:
            conn.commit()
            return True, "密码重置成功"
        else:
            return False, "用户不存在"
            
    except Exception as e:
        print(f"Error resetting password: {str(e)}")
        return False, f"密码重置失败: {str(e)}"
    finally:
        conn.close()

def hash_password(password):
    """加密密码"""
    try:
        hashed = bcrypt.hash(password)
        print(f"Password hashed successfully")  # 调试日志
        return hashed
    except Exception as e:
        print(f"Password hashing error: {str(e)}")
        raise e

def verify_password(password, hashed):
    """验证密码"""
    try:
        result = bcrypt.verify(password, hashed)
        print(f"Password verification result: {result}")  # 调试日志
        return result
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False

# 验证码相关函数
def store_verification_code(email, code):
    """存储验证码"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 删除旧的验证码
    cursor.execute('DELETE FROM verification_codes WHERE email = ?', (email,))
    
    # 插入新验证码
    expires_at = datetime.datetime.now() + datetime.timedelta(
        minutes=Config.VERIFICATION_CODE_EXPIRY_MINUTES
    )
    cursor.execute('''
        INSERT INTO verification_codes (email, code, expires_at)
        VALUES (?, ?, ?)
    ''', (email, code, expires_at))
    
    conn.commit()
    conn.close()

def get_verification_code(email):
    """获取有效的验证码"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT code FROM verification_codes 
        WHERE email = ? AND expires_at > ? 
        ORDER BY created_at DESC LIMIT 1
    ''', (email, datetime.datetime.now()))
    
    result = cursor.fetchone()
    conn.close()
    return result['code'] if result else None

def invalidate_verification_code(email, code):
    """使验证码失效"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM verification_codes 
        WHERE email = ? AND code = ?
    ''', (email, code))
    conn.commit()
    conn.close()

# Token黑名单相关函数
def add_token_to_blacklist(token):
    """将token添加到黑名单"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO token_blacklist (token)
            VALUES (?)
        ''', (token,))
        conn.commit()
    except Exception:
        pass  # 忽略重复插入错误
    finally:
        conn.close()

def is_token_blacklisted(token):
    """检查token是否在黑名单中"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM token_blacklist WHERE token = ?', (token,))
    result = cursor.fetchone()
    conn.close()
    return bool(result)

def update_user_info(user_id, nickname, phone=None, email=None):
    """更新用户信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查昵称是否被其他用户使用
        cursor.execute('SELECT id FROM users WHERE nickname = ? AND id != ?', (nickname, user_id))
        if cursor.fetchone():
            return None, "昵称已被使用"
        
        # 检查邮箱是否被其他用户使用
        if email:
            cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, user_id))
            if cursor.fetchone():
                return None, "邮箱已被其他用户使用"
        
        # 检查手机号是否被其他用户使用
        if phone:
            cursor.execute('SELECT id FROM users WHERE phone = ? AND id != ?', (phone, user_id))
            if cursor.fetchone():
                return None, "手机号已被其他用户使用"
        
        # 构建更新SQL
        update_fields = ['nickname = ?']
        update_values = [nickname]
        
        if phone is not None:
            update_fields.append('phone = ?')
            update_values.append(phone)
        
        if email is not None:
            update_fields.append('email = ?')
            update_values.append(email)
        
        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        update_values.append(user_id)
        
        # 执行更新
        cursor.execute(f'''
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = ?
        ''', update_values)
        
        # 获取更新后的用户信息
        cursor.execute('''
            SELECT id, nickname, phone, email, avatar, role, created_at, updated_at
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.commit()
        
        if user:
            return dict(user), "用户信息更新成功"
        else:
            return None, "用户不存在"
            
    except sqlite3.IntegrityError as e:
        return None, f"数据完整性错误: {str(e)}"
    except Exception as e:
        print(f"Error updating user info: {str(e)}")
        return None, f"更新失败: {str(e)}"
    finally:
        conn.close()

def change_user_password(user_id, old_password, new_password):
    """修改用户密码"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取用户当前密码
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return False, "用户不存在"
        
        # 验证原密码
        if not verify_password(old_password, user['password_hash']):
            return False, "原密码错误"
        
        # 加密新密码
        new_password_hash = bcrypt.hash(new_password)
        
        # 更新密码
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (new_password_hash, user_id))
        
        conn.commit()
        return True, "密码修改成功"
        
    except Exception as e:
        print(f"Error changing password: {str(e)}")
        return False, f"密码修改失败: {str(e)}"
    finally:
        conn.close()

def update_user_avatar(user_id, avatar_url):
    """更新用户头像"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET avatar = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (avatar_url, user_id))
        
        conn.commit()
        
        # 获取更新后的用户信息
        cursor.execute('''
            SELECT id, nickname, phone, email, avatar, role
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        return dict(user) if user else None, "头像更新成功"
        
    except Exception as e:
        print(f"Error updating avatar: {str(e)}")
        return None, f"头像更新失败: {str(e)}"
    finally:
        conn.close()

def get_user_info(user_id):
    """获取用户详细信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, nickname, phone, email, avatar, role, created_at, updated_at
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        return dict(user) if user else None
        
    except Exception as e:
        print(f"Error getting user info: {str(e)}")
        return None
    finally:
        conn.close()