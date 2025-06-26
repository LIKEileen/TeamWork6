# Author: 唐震
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.config import Config
import logging
import os

def create_app():
    """应用工厂函数"""
    # 初始化 Flask 应用
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 启用 CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 确保上传目录存在
    upload_dirs = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'avatars')
    ]
    
    for upload_dir in upload_dirs:
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            logging.info(f"Created upload directory: {upload_dir}")
    
    # 配置静态文件服务
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """提供上传文件访问"""
        upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        return send_from_directory(upload_path, filename)
    
    @app.route('/uploads/avatars/<filename>')
    def uploaded_avatar(filename):
        """提供头像文件访问"""
        upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'avatars')
        return send_from_directory(upload_path, filename)
    
    # 添加错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {
            'code': 0,
            'message': '请求的资源不存在',
            'data': {}
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"Internal server error: {str(error)}")
        return {
            'code': 0,
            'message': '服务器内部错误',
            'data': {}
        }, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {
            'code': 0,
            'message': '请求参数错误',
            'data': {}
        }, 400
    
    # 添加根路径路由
    @app.route('/')
    def home():
        return {
            'code': 1,
            'message': 'Schedule Planner API is running',
            'data': {
                'version': '1.0.0',
                'endpoints': [
                    '/api/register',
                    '/api/login',
                    '/api/logout',
                    '/api/send-verification-code',
                    '/api/bind',
                    '/api/reset-password'
                ]
            }
        }
    
    # 添加健康检查路由
    @app.route('/health')
    def health_check():
        return {
            'code': 1,
            'message': 'Service is healthy',
            'data': {'status': 'ok'}
        }
    
    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.schedule import schedule_bp
    from .routes.meeting import meeting_bp
    from .routes.upload import upload_bp
    from .routes.organization import organization_bp  # 新增组织路由
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(schedule_bp, url_prefix='/api')
    app.register_blueprint(meeting_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(organization_bp, url_prefix='/api')  # 注册组织路由
    
    # 初始化数据库（应用启动时执行一次）
    with app.app_context():
        try:
            from app.models.user import init_db
            init_db()
            logging.info("User database initialized")
        except Exception as e:
            logging.error(f"Failed to initialize user database: {str(e)}")
        
        try:
            from app.models.schedule import init_schedule_db
            init_schedule_db()
            logging.info("Schedule database initialized")
        except Exception as e:
            logging.error(f"Failed to initialize schedule database: {str(e)}")
        
        try:
            from app.models.organization import init_organization_db  # 新增组织数据库初始化
            init_organization_db()
            logging.info("Organization database initialized")
        except Exception as e:
            logging.error(f"Failed to initialize organization database: {str(e)}")

        try:
            from app.models.meeting import init_meeting_db
            init_meeting_db()
            logging.info("Meeting database initialized")
        except Exception as e:
            logging.error(f"Failed to initialize meeting database: {str(e)}")
    
    return app

# 创建应用实例
app = create_app()