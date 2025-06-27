import pytest
import sqlite3
import datetime
from werkzeug.security import generate_password_hash

# 导入所有数据库初始化函数
from app.models.user import init_db as init_user_db
from app.models.meeting import init_meeting_db
# 假设你的组织模型文件路径是 app/models/organization.py
from app.models.organization import init_organization_db

@pytest.fixture(scope="function")
def setup_databases(monkeypatch):
    """
    一个全面的 Fixture，用于设置所有需要的内存数据库。
    - 创建独立的内存数据库用于用户/会议和组织。
    - Monkeypatch 所有 get_db_connection 函数以使用这些内存数据库。
    - 初始化所有表结构。
    - 填充虚拟数据。
    - 在每次测试后清理。
    
    使用 scope="function" 确保每个测试函数都获得一个全新的、干净的数据库。
    """
    # 1. 创建两个独立的内存数据库连接
    main_db_conn = sqlite3.connect(":memory:")
    main_db_conn.row_factory = sqlite3.Row
    
    org_db_conn = sqlite3.connect(":memory:")
    org_db_conn.row_factory = sqlite3.Row

    # 2. (关键!) Monkeypatch 所有数据库连接函数
    #    - user.py 和 meeting.py 使用 main_db_conn
    monkeypatch.setattr("app.models.user.get_db_connection", lambda: main_db_conn)
    monkeypatch.setattr("app.models.meeting.get_db_connection", lambda: main_db_conn)
    #    - organization.py 有两个不同的连接函数
    monkeypatch.setattr("app.models.organization.get_db_connection", lambda: org_db_conn)
    monkeypatch.setattr("app.models.organization.get_user_db_connection", lambda: main_db_conn)
    
    # 3. 初始化所有数据库表
    init_user_db()
    init_meeting_db()
    init_organization_db()

    # 4. 填充虚拟数据
    main_cursor = main_db_conn.cursor()
    org_cursor = org_db_conn.cursor()

    # 填充用户数据
    users_to_add = [
        (1, 'Creator_One', '11111111111', 'creator1@test.com', generate_password_hash('pass1'), 'avatar1.jpg', 'user'),
        (2, 'Admin_Two', '22222222222', 'admin2@test.com', generate_password_hash('pass2'), 'avatar2.jpg', 'user'),
        (3, 'Member_Three', '33333333333', 'member3@test.com', generate_password_hash('pass3'), 'avatar3.jpg', 'user'),
        (4, 'Applicant_Four', '44444444444', 'applicant4@test.com', generate_password_hash('pass4'), 'avatar4.jpg', 'user'),
        (5, 'Invitee_Five', '55555555555', 'invitee5@test.com', generate_password_hash('pass5'), 'avatar5.jpg', 'user'),
    ]
    main_cursor.executemany("INSERT INTO users (id, nickname, phone, email, password_hash, avatar, role) VALUES (?, ?, ?, ?, ?, ?, ?)", users_to_add)
    main_db_conn.commit()

    # 填充组织数据
    orgs_to_add = [
        ('org_1', 'Test Org One', '1'), # creator_id is '1'
        ('org_2', 'Test Org Two', '2'), # creator_id is '2'
    ]
    org_cursor.executemany("INSERT INTO organizations (id, name, creator_id) VALUES (?, ?, ?)", orgs_to_add)

    # 填充组织成员数据
    members_to_add = [
        ('org_1', '1', 'creator'),
        ('org_1', '2', 'admin'),
        ('org_1', '3', ''), # 普通成员
        ('org_2', '2', 'creator'),
    ]
    org_cursor.executemany("INSERT INTO organization_members (org_id, user_id, role) VALUES (?, ?, ?)", members_to_add)
    org_db_conn.commit()
    
    # 使用 yield 将数据库连接字典提供给测试函数
    yield {
        "main_db": main_db_conn,
        "org_db": org_db_conn
    }

    # 测试结束后，清理工作会自动执行
    main_db_conn.close()
    org_db_conn.close()
