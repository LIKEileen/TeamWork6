import sqlite3
from passlib.hash import bcrypt
import datetime
import os
from ..config import Config
import logging

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # 支持字典式访问
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise

def init_db():
    """初始化用户数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL,
                phone TEXT UNIQUE,
                email TEXT UNIQUE NOT NULL,
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
        logging.info("Database tables initialized successfully")
        
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

def hash_password(password):
    """加密密码"""
    try:
        hashed = bcrypt.hash(password)
        logging.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logging.error(f"Password hashing error: {str(e)}")
        raise e

def verify_password(password, hashed):
    """验证密码"""
    try:
        result = bcrypt.verify(password, hashed)
        logging.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logging.error(f"Password verification error: {str(e)}")
        return False

def store_verification_code(email, code):
    """存储验证码"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
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
        logging.info(f"Verification code stored for email: {email}")
        
    except Exception as e:
        logging.error(f"Error storing verification code: {str(e)}")
        raise
    finally:
        conn.close()

def get_verification_code(email):
    """获取有效的验证码"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT code FROM verification_codes 
            WHERE email = ? AND expires_at > ? 
            ORDER BY created_at DESC LIMIT 1
        ''', (email, datetime.datetime.now()))
        
        result = cursor.fetchone()
        return result['code'] if result else None
        
    except Exception as e:
        logging.error(f"Error getting verification code: {str(e)}")
        return None
    finally:
        conn.close()

def invalidate_verification_code(email, code):
    """使验证码失效"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            DELETE FROM verification_codes 
            WHERE email = ? AND code = ?
        ''', (email, code))
        conn.commit()
        logging.info(f"Verification code invalidated for email: {email}")
        
    except Exception as e:
        logging.error(f"Error invalidating verification code: {str(e)}")
    finally:
        conn.close()

def create_user(user_data):
    """创建新用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        logging.info(f"Creating user with data: {user_data}")
        
        # 提取用户数据
        nickname = user_data.get('nickname')
        phone = user_data.get('phone')
        email = user_data.get('email')
        password_hash = user_data.get('password_hash')
        avatar = user_data.get('avatar', Config.DEFAULT_AVATAR_URL)
        role = user_data.get('role', 'user')
        
        # 验证必填字段
        if not all([nickname, email, password_hash]):
            return None, "昵称、邮箱和密码不能为空"
        
        # 检查邮箱是否已存在
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return None, "该邮箱已被注册"
        
        # 检查手机号是否已存在（如果提供了手机号）
        if phone:
            cursor.execute('SELECT id FROM users WHERE phone = ?', (phone,))
            if cursor.fetchone():
                return None, "该手机号已被注册"
        
        # 插入新用户
        cursor.execute('''
            INSERT INTO users (nickname, phone, email, password_hash, avatar, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nickname, phone, email, password_hash, avatar, role))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # 获取创建的用户信息
        cursor.execute('''
            SELECT id, nickname, phone, email, password_hash, avatar, role, created_at, updated_at
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        if user:
            user_dict = dict(user)
            logging.info(f"User created successfully: ID={user_dict['id']}")
            return user_dict, "用户创建成功"
        else:
            return None, "用户创建失败"
        
    except sqlite3.IntegrityError as e:
        logging.error(f"Database integrity error: {str(e)}")
        if "phone" in str(e):
            return None, "该手机号已被注册"
        elif "email" in str(e):
            return None, "该邮箱已被注册"
        else:
            return None, "数据完整性错误"
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return None, f"创建用户失败: {str(e)}"
    finally:
        conn.close()

def get_user_by_phone_or_email(phone=None, email=None):
    """通过手机号或邮箱获取用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if phone:
            logging.info(f"Searching user by phone: {phone}")
            cursor.execute('''
                SELECT id, nickname, phone, email, password_hash, avatar, role, created_at, updated_at
                FROM users WHERE phone = ?
            ''', (phone,))
        elif email:
            logging.info(f"Searching user by email: {email}")
            cursor.execute('''
                SELECT id, nickname, phone, email, password_hash, avatar, role, created_at, updated_at
                FROM users WHERE email = ?
            ''', (email,))
        else:
            return None
        
        user = cursor.fetchone()
        logging.debug(f"Database query result: {dict(user) if user else None}")
        
        return dict(user) if user else None
        
    except Exception as e:
        logging.error(f"Error getting user: {str(e)}")
        return None
    finally:
        conn.close()

def get_user_by_id(user_id):
    """根据用户ID获取用户信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, nickname, phone, email, password_hash, avatar, role, created_at, updated_at
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        return dict(user) if user else None
        
    except Exception as e:
        logging.error(f"Error getting user by id: {str(e)}")
        return None
    finally:
        conn.close()

def bind_phone(user_id, phone):
    """绑定用户手机号"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查手机号是否已被其他用户使用
        cursor.execute('SELECT id FROM users WHERE phone = ? AND id != ?', (phone, user_id))
        if cursor.fetchone():
            return None, "该手机号已被其他用户绑定"
        
        # 更新用户手机号
        cursor.execute('''
            UPDATE users SET phone = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (phone, user_id))
        
        if cursor.rowcount == 0:
            return None, "用户不存在"
        
        conn.commit()
        
        # 获取更新后的用户信息
        cursor.execute('''
            SELECT id, nickname, phone, email, password_hash, avatar, role, created_at, updated_at
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        return dict(user) if user else None, "手机号绑定成功"
        
    except sqlite3.IntegrityError as e:
        logging.error(f"Phone binding integrity error: {str(e)}")
        return None, "该手机号已被使用"
    except Exception as e:
        logging.error(f"Error binding phone: {str(e)}")
        return None, f"绑定手机号失败: {str(e)}"
    finally:
        conn.close()

def update_user_info(user_id, updates):
    """更新用户信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 构建更新语句
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key in ['nickname', 'avatar', 'role']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return None, "没有可更新的字段"
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            return None, "用户不存在"
        
        conn.commit()
        
        # 获取更新后的用户信息
        updated_user = get_user_by_id(user_id)
        return updated_user, "用户信息更新成功"
        
    except Exception as e:
        logging.error(f"Error updating user info: {str(e)}")
        return None, f"更新用户信息失败: {str(e)}"
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
        
        # 验证旧密码
        if not bcrypt.verify(old_password, user['password_hash']):
            return False, "原密码错误"
        
        # 更新密码
        new_password_hash = bcrypt.hash(new_password)
        cursor.execute('''
            UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (new_password_hash, user_id))
        
        conn.commit()
        return True, "密码修改成功"
        
    except Exception as e:
        logging.error(f"Error changing password: {str(e)}")
        return False, f"密码修改失败: {str(e)}"
    finally:
        conn.close()

def update_user_avatar(user_id, avatar_url):
    """更新用户头像"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users SET avatar = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (avatar_url, user_id))
        
        if cursor.rowcount == 0:
            return None, "用户不存在"
        
        conn.commit()
        
        # 获取更新后的用户信息
        updated_user = get_user_by_id(user_id)
        return updated_user, "头像更新成功"
        
    except Exception as e:
        logging.error(f"Error updating avatar: {str(e)}")
        return None, f"头像更新失败: {str(e)}"
    finally:
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