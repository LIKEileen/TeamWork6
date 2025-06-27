import pytest
import datetime
# 导入需要被测试的函数
from app.models.meeting import (
    init_meeting_db,
    create_meeting_in_db,
    get_meetings_by_user_id,
)

def test_init_meeting_db(test_db):
    """
    测试数据库初始化函数是否成功创建了'meetings'和'meeting_participants'表。
    它接收 test_db fixture，这个fixture已经完成了初始化。
    我们只需验证结果即可。
    """
    cursor = test_db.cursor()
    
    # 检查 'meetings' 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meetings'")
    table = cursor.fetchone()
    assert table is not None, "The 'meetings' table should be created."

    # 检查 'meeting_participants' 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meeting_participants'")
    table = cursor.fetchone()
    assert table is not None, "The 'meeting_participants' table should be created."

    # 检查索引是否被创建
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_meeting_creator'")
    index = cursor.fetchone()
    assert index is not None, "Index on meetings(creator_id) should exist."


def test_create_meeting_in_db(seed_data):
    """
    测试创建会议的功能。
    它接收 seed_data fixture，该 fixture 提供了已填充数据的数据库。
    """
    # 准备新会议的数据
    new_meeting_data = {
        "title": "New Planning Session",
        "description": "Planning for Q4",
        "start_time": "2025-08-01 10:00:00",
        "end_time": "2025-08-01 12:00:00",
        "min_participants": 2,
    }
    creator_id = 1
    participant_ids = [2]
    key_participant_ids = [1, 2] # 创建者和参与者2都是关键成员

    # 调用函数创建会议
    created_meeting, message = create_meeting_in_db(
        new_meeting_data, creator_id, participant_ids, key_participant_ids
    )

    # 验证返回结果
    assert message == "会议创建成功"
    assert created_meeting is not None
    assert created_meeting["title"] == "New Planning Session"
    assert created_meeting["creator_id"] == 1
    new_meeting_id = created_meeting["id"]

    # 直接查询数据库进行最终验证
    cursor = seed_data.cursor()
    
    # 验证会议已插入 meetings 表
    cursor.execute("SELECT * FROM meetings WHERE id = ?", (new_meeting_id,))
    meeting_in_db = cursor.fetchone()
    assert meeting_in_db is not None
    assert meeting_in_db["description"] == "Planning for Q4"

    # 验证所有参与者都已正确插入 meeting_participants 表
    cursor.execute("SELECT * FROM meeting_participants WHERE meeting_id = ?", (new_meeting_id,))
    participants_in_db = cursor.fetchall()
    # 参与者应该是 creator_id (1) 和 participant_ids ([2]) 的并集，共2人
    assert len(participants_in_db) == 2 
    
    participant_map = {row['user_id']: row for row in participants_in_db}
    assert 1 in participant_map # 检查创建者是否在内
    assert 2 in participant_map # 检查普通参与者是否在内
    assert participant_map[1]['is_key_member'] == 1 # 1 is True for SQLite BOOLEAN
    assert participant_map[2]['is_key_member'] == 1


def test_get_meetings_by_user_id(seed_data):
    """
    测试根据用户ID获取会议列表的功能。
    """
    # === 测试场景1: 用户1应该能看到2个会议 (Past 和 Future) ===
    meetings_user1 = get_meetings_by_user_id(user_id=1)
    assert len(meetings_user1) == 2
    # 检查返回的会议标题
    titles_user1 = {m['title'] for m in meetings_user1}
    assert "Past Meeting" in titles_user1
    assert "Future Meeting" in titles_user1
    
    # 检查一个会议的参与者列表是否正确
    future_meeting = next(m for m in meetings_user1 if m['title'] == 'Future Meeting')
    assert len(future_meeting['participants']) == 3

    # === 测试场景2: 用户3应该只能看到1个会议 (Today) ===
    meetings_user3 = get_meetings_by_user_id(user_id=3)
    assert len(meetings_user3) == 1
    assert meetings_user3[0]['title'] == 'Today Meeting'

    # === 测试场景3: 日期过滤 - 只查找2025年1月的会议 ===
    start_date = datetime.date(2025, 1, 1)
    end_date = datetime.date(2025, 1, 31)
    meetings_jan = get_meetings_by_user_id(user_id=1, start_date=start_date, end_date=end_date)
    assert len(meetings_jan) == 1
    assert meetings_jan[0]['title'] == 'Past Meeting'

    # === 测试场景4: 日期过滤 - 查找所有会议 ===
    all_meetings = get_meetings_by_user_id(user_id=1, start_date=datetime.date(2025, 1, 1), end_date=datetime.date(2025, 12, 31))
    assert len(all_meetings) == 2

    # === 测试场景5: 一个没有任何会议的用户应该返回空列表 ===
    # 假设用户 99 不存在于任何会议中
    no_meetings_user = get_meetings_by_user_id(user_id=99)
    assert no_meetings_user == []

