import pytest
import sqlite3
import datetime
from werkzeug.security import generate_password_hash
from flask import Flask
import json

# 导入所有数据库初始化函数
from app.models.user import init_db as init_user_db
from app.models.meeting import init_meeting_db
from app.models.organization import init_organization_db
from app.models.schedule import init_schedule_db
# 导入需要被测试的蓝图
from app.routes.auth import auth_bp
from app.routes.meeting import meeting_bp
from app.routes.organization import organization_bp
from app.routes.schedule import schedule_bp
from app.routes.upload import upload_bp
from app.routes.user import user_bp # 新增导入

@pytest.fixture(scope="function")
def setup_databases(monkeypatch):
    """
    一个全面的 Fixture，用于设置所有需要的内存数据库。
    """
    # 1. 创建独立的内存数据库连接
    main_db_conn = sqlite3.connect(":memory:")
    main_db_conn.row_factory = sqlite3.Row
    
    org_db_conn = sqlite3.connect(":memory:")
    org_db_conn.row_factory = sqlite3.Row

    # 2. (关键!) Monkeypatch 所有数据库连接函数
    monkeypatch.setattr("app.models.user.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.models.meeting.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.models.schedule.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.models.organization.get_db_connection", lambda: org_db_conn)
    monkeypatch.setattr("app.models.organization.get_user_db_connection", lambda: main_db_conn)
    # 为所有 service 层添加 patch
    monkeypatch.setattr("app.services.auth_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.verification_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.meeting_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.organization_service.get_db_connection", lambda: org_db_conn)
    monkeypatch.setattr("app.services.organization_service.get_user_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.schedule_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.upload_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.user_service.get_db_connection", lambda: main_db_conn) # 新增 patch

    # 3. 初始化所有数据库表
    init_user_db()
    init_meeting_db()
    init_organization_db()
    init_schedule_db()

    # 4. 填充虚拟数据
    main_cursor = main_db_conn.cursor()

    # 填充用户数据
    users_to_add = [
        (1, 'Creator_One', '11111111111', 'creator1@test.com', generate_password_hash('pass1'), 'avatar1.jpg', 'user'),
        (2, 'Admin_Two', '22222222222', 'admin2@test.com', generate_password_hash('pass2'), 'avatar2.jpg', 'user'),
    ]
    main_cursor.executemany("INSERT INTO users (id, nickname, phone, email, password_hash, avatar, role) VALUES (?, ?, ?, ?, ?, ?, ?)", users_to_add)
    main_db_conn.commit()
    
    yield { "main_db": main_db_conn, "org_db": org_db_conn }

    main_db_conn.close()
    org_db_conn.close()

@pytest.fixture
def test_client(setup_databases):
    """
    创建一个用于测试 Flask 应用的客户端。
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'my-super-secret-test-key'
    app.config['TESTING'] = True
    
    # 注册所有需要测试的蓝图
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(meeting_bp)
    app.register_blueprint(organization_bp)
    app.register_blueprint(schedule_bp, url_prefix='/schedule')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(user_bp) # 新增注册

    with app.test_client() as client:
        yield client

def _get_token(test_client, email, password):
    """辅助函数，用于登录并获取token。"""
    login_response = test_client.post('/auth/login', json={"email": email, "password": password})
    return login_response.get_json()['data']['token']

@pytest.fixture
def authed_token(test_client):
    """为用户1提供有效的JWT Token。"""
    return _get_token(test_client, 'creator1@test.com', 'pass1')

