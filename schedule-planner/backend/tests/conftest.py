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
# 导入所有需要被测试的蓝图
from app.routes.auth import auth_bp
from app.routes.meeting import meeting_bp
from app.routes.organization import organization_bp
from app.routes.schedule import schedule_bp
from app.routes.upload import upload_bp
from app.routes.user import user_bp

@pytest.fixture(scope="function")
def setup_databases(monkeypatch):
    """
    一个全面的 Fixture，用于设置所有需要的内存数据库。
    - 创建独立的内存数据库用于用户/会议/日程和组织。
    - Monkeypatch 所有 get_db_connection 函数以使用这些内存数据库。
    - 初始化所有表结构。
    - 填充所有虚拟数据。
    - 在每次测试后清理。
    """
    # 1. 创建独立的内存数据库连接
    main_db_conn = sqlite3.connect(":memory:")
    main_db_conn.row_factory = sqlite3.Row
    
    org_db_conn = sqlite3.connect(":memory:")
    org_db_conn.row_factory = sqlite3.Row

    # 2. (关键!) Monkeypatch 所有数据库连接函数
    # 模型层
    monkeypatch.setattr("app.models.user.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.models.meeting.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.models.schedule.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.models.organization.get_db_connection", lambda: org_db_conn)
    monkeypatch.setattr("app.models.organization.get_user_db_connection", lambda: main_db_conn)
    # 服务层
    monkeypatch.setattr("app.services.auth_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.verification_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.meeting_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.organization_service.get_db_connection", lambda: org_db_conn)
    monkeypatch.setattr("app.services.organization_service.get_user_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.schedule_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.upload_service.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.services.user_service.get_db_connection", lambda: main_db_conn)

    # 3. 初始化所有数据库表
    init_user_db()
    init_meeting_db()
    init_organization_db()
    init_schedule_db()

    # 4. 填充虚拟数据
    main_cursor = main_db_conn.cursor()
    org_cursor = org_db_conn.cursor()

    # 填充用户数据
    users_to_add = [
        (1, 'Creator_One', '11111111111', 'creator1@test.com', generate_password_hash('pass1'), 'avatar1.jpg', 'user'),
        (2, 'Admin_Two', '22222222222', 'admin2@test.com', generate_password_hash('pass2'), 'avatar2.jpg', 'user'),
        (3, 'Member_Three', '33333333333', 'member3@test.com', generate_password_hash('pass3'), 'avatar3.jpg', 'user'),
        (4, 'Outsider_Four', '44444444444', 'outsider4@test.com', generate_password_hash('pass4'), 'avatar4.jpg', 'user'),
    ]
    main_cursor.executemany("INSERT INTO users (id, nickname, phone, email, password_hash, avatar, role) VALUES (?, ?, ?, ?, ?, ?, ?)", users_to_add)

    # 填充日程数据
    schedule_events_to_add = [
        (1, 1, 'Morning Standup', '2025-06-27', '09:00', '09:30', '#409EFF'),
        (2, 1, 'Lunch with Team', '2025-06-27', '12:00', '13:00', '#67C23A'),
    ]
    main_cursor.executemany("INSERT INTO schedule_events (id, user_id, title, day, start_time, end_time, color) VALUES (?, ?, ?, ?, ?, ?, ?)", schedule_events_to_add)

    # 填充会议数据
    meetings_to_add = [
        (1, 'Past Meeting', 'A meeting in the past', '2025-01-10 10:00:00', '2025-01-10 11:00:00', 1, 2),
    ]
    main_cursor.executemany("INSERT INTO meetings (id, title, description, start_time, end_time, creator_id, min_participants) VALUES (?, ?, ?, ?, ?, ?, ?)", meetings_to_add)
    
    # 填充会议参与者数据
    participants_to_add = [(1, 1, 'accepted', True), (1, 2, 'pending', False)]
    main_cursor.executemany("INSERT INTO meeting_participants (meeting_id, user_id, status, is_key_member) VALUES (?, ?, ?, ?)", participants_to_add)
    main_db_conn.commit()

    # 填充组织数据
    orgs_to_add = [('org_1', 'Test Org One', '1')]
    org_cursor.executemany("INSERT INTO organizations (id, name, creator_id) VALUES (?, ?, ?)", orgs_to_add)
    
    # 填充组织成员数据
    members_to_add = [('org_1', '1', 'creator'), ('org_1', '2', 'admin'), ('org_1', '3', '')]
    org_cursor.executemany("INSERT INTO organization_members (org_id, user_id, role) VALUES (?, ?, ?)", members_to_add)
    org_db_conn.commit()
    
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
    app.register_blueprint(user_bp)

    with app.test_client() as client:
        yield client

def _get_token(test_client, email, password):
    """辅助函数，用于登录并获取token。"""
    login_response = test_client.post('/auth/login', json={"email": email, "password": password})
    # 添加一个检查，以防登录失败
    if login_response.status_code != 200:
        return None
    return login_response.get_json()['data']['token']

@pytest.fixture
def creator_token(test_client):
    """为组织创建者(user 1)提供有效的JWT Token。"""
    return _get_token(test_client, 'creator1@test.com', 'pass1')

@pytest.fixture
def admin_token(test_client):
    """为组织管理员(user 2)提供有效的JWT Token。"""
    return _get_token(test_client, 'admin2@test.com', 'pass2')

@pytest.fixture
def member_token(test_client):
    """为普通成员(user 3)提供有效的JWT Token。"""
    return _get_token(test_client, 'member3@test.com', 'pass3')

@pytest.fixture
def outsider_token(test_client):
    """为组织外成员(user 4)提供有效的JWT Token。"""
    return _get_token(test_client, 'outsider4@test.com', 'pass4')

