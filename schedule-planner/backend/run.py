from app import create_app
from app.models.user import init_db
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    # 初始化数据库
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
    
    # 创建应用
    app = create_app()
    
    # 启动应用
    app.run(host='0.0.0.0', port=5000, debug=True)