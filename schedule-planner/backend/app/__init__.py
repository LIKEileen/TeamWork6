from flask import Flask, send_from_directory
from flask_cors import CORS
from app.routes.auth import auth_bp
from app.routes.schedule import schedule_bp
from app.routes.user import user_bp  # 新增
from app.config import Config
import logging
import os

# 初始化 Flask 应用
app = Flask(__name__)
app.config.from_object(Config)

# 配置日志
logging.basicConfig(level=logging.DEBUG)

# 启用 CORS
CORS(app)

# 配置静态文件服务（用于头像访问）
@app.route('/uploads/avatars/<filename>')
def uploaded_avatar(filename):
    """提供头像文件访问"""
    return send_from_directory('uploads/avatars', filename)

# 添加根路径路由
@app.route('/')
def home():
    return {
        'message': 'Schedule Planner API Server',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': {
                'login': '/api/login',
                'register': '/api/register',
                'bind': '/api/bind',
                'send_verification_code': '/api/send-verification-code',
                'reset_password': '/api/reset-password',
                'logout': '/api/logout'
            },
            'schedule': {
                'get_schedule': '/api/user/schedule',
                'add_event': '/api/user/schedule/add',
                'add_recurring': '/api/user/schedule/add/recurring',
                'delete_event': '/api/user/schedule/delete',
                'import_excel': '/api/user/schedule/import/excel',
                'import_school': '/api/user/schedule/import/school'
            },
            'user': {
                'update': '/api/user/update',
                'change_password': '/api/user/change-password',
                'upload_avatar': '/api/user/avatar/upload',
                'profile': '/api/user/profile'
            }
        }
    }

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(schedule_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')  # 新增

# 初始化数据库（应用启动时执行一次）
from app.models.user import init_db
from app.models.schedule import init_schedule_db
init_db()
init_schedule_db()