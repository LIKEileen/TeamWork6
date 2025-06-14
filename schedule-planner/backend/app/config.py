# Author: 唐震
import os

class Config:
    # JWT 配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_EXPIRATION_HOURS = 24
    
    # 密码配置
    PASSWORD_MIN_LENGTH = 6
    PASSWORD_HASH_METHOD = 'pbkdf2:sha256'  # werkzeug 默认方法
    
    # 数据库配置
    DATABASE_PATH = 'schedule_planner.db'  # 确保这个属性存在
    DATABASE_URL = 'schedule_planner.db'   # 保持兼容性
    
    # 默认头像配置
    DEFAULT_AVATAR_URL = "https://imgheybox.max-c.com/bbs/2024/09/19/1dc7d8a7978e8e9be26498747ef493ce/thumb.png"
    
    # 验证码配置
    VERIFICATION_CODE_LENGTH = 6
    VERIFICATION_CODE_EXPIRY_MINUTES = 5
    
    # 邮件服务配置
    EMAIL_CONFIG = {
        'smtp_server': 'smtp.qq.com',  # QQ邮箱
        'smtp_port': 587,
        'sender_email': '3426411644@qq.com',  # 替换为真实邮箱
        'sender_password': 'rvmqpwlsurfwdbaj',   # 不是QQ密码，是授权码！
        'sender_name': 'Schedule Planner'
    }
    
    # 上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB