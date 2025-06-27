import pytest
from datetime import datetime, date, time
from app.services.meeting_service import (
    find_meeting_times,
    create_meeting,
    get_user_meetings,
    # 导入内部函数以便进行单元测试
    _merge_start_minutes_to_slots,
    _get_remaining_work_time,
    _get_free_time,
    _recursive_find,
)
from app.models.user import get_user_by_id

# --- 内部工具函数的单元测试 ---
# 这些测试不依赖数据库，因此不需要 fixture

def test_merge_start_minutes_to_slots():
    """测试将连续的开始时间点合并为时间段的工具函数。"""
    # 场景1: 连续的时间点
    minutes = [600, 601, 602, 603] # 10:00, 10:01, 10:02, 10:03
    duration = 30
    result = _merge_start_minutes_to_slots(minutes, duration)
    # 应该合并成一个从 10:00 开始，到 10:03 + 30 分钟 = 10:33 结束的时间段
    assert result == [(600, 633)]

    # 场景2: 不连续的时间点
    minutes = [600, 601, 630, 631]
    result = _merge_start_minutes_to_slots(minutes, duration)
    # 应该产生两个时间段
    assert result == [(600, 631), (630, 661)]

    # 场景3: 空列表
    assert _merge_start_minutes_to_slots([], duration) == []

def test_get_remaining_work_time(mocker):
    """测试计算剩余工作时间的工具函数。"""
    # 固定当前日期和时间以进行可预测的测试
    fixed_now = datetime(2025, 6, 27, 10, 30) # 周五, 10:30 AM
    mocker.patch('app.services.meeting_service.datetime.now', return_value=fixed_now)
    
    start_date = date(2025, 6, 27)
    end_date = date(2025, 6, 28) # 周六，非工作日

    # 默认工作时间是 9:00 - 17:00 (540 - 1020 分钟)
    result = _get_remaining_work_time(start_date, end_date)

    # 应该只包含周五的结果
    assert '2025-06-27' in result
    assert '2025-06-28' not in result
    
    # 周五的剩余工作时间应从当前时间 10:30 (630分钟) 开始
    assert result['2025-06-27'] == [(630, 1020)]


# --- 依赖数据库的服务层函数的集成测试 ---

def test_get_user_meetings_service(setup_databases):
    """测试获取用户会议列表的服务。"""
    # conftest 中为用户1预置了会议 'Past Meeting'
    meetings, message = get_user_meetings(user_id=1)
    
    assert "获取成功" in message
    assert len(meetings) > 0
    assert meetings[0]['title'] == 'Past Meeting'

def test_create_meeting_service_success(setup_databases):
    """测试成功创建会议的服务。"""
    creator_id = 1
    meeting_data = {
        "title": "Service Layer Test Meeting",
        "start_time": "2025-09-01T10:00:00Z",
        "end_time": "2025-09-01T11:00:00Z",
        "participants": ["creator1@test.com", "admin2@test.com"],
        "key_participants": ["creator1@test.com"]
    }

    meeting, message = create_meeting(meeting_data, creator_id)

    assert "会议创建成功" in message
    assert meeting is not None
    assert meeting['title'] == "Service Layer Test Meeting"
    assert meeting['creator_id'] == creator_id
    # 验证参与者信息是否被正确添加
    assert len(meeting['participants']) == 2


def test_create_meeting_service_user_not_found(setup_databases):
    """测试创建会议时有参与者未找到的场景。"""
    creator_id = 1
    meeting_data = {
        "title": "Invalid Participant Meeting",
        "start_time": "2025-09-02T10:00:00Z",
        "end_time": "2025-09-02T11:00:00Z",
        "participants": ["creator1@test.com", "nonexistent@user.com"],
        "key_participants": []
    }

    meeting, message = create_meeting(meeting_data, creator_id)

    assert meeting is None
    assert "以下普通参与者未找到: nonexistent@user.com" in message


def test_find_meeting_times_service(setup_databases):
    """
    测试查找可用会议时间的核心服务。
    这个测试会利用 conftest 中为用户1和2设置的日程和会议来模拟忙碌时间。
    """
    # 查找用户1和用户2在 2025-06-27 当天的共同空闲时间，时长60分钟
    participants = ["creator1@test.com", "admin2@test.com"]
    key_participants = []
    duration = 60
    start_date_str = "2025-06-27"
    end_date_str = "2025-06-27"

    # 预期的忙碌时间 (默认工作时间 9:00 - 17:00):
    # 用户1: 09:00-09:30 (日程), 12:00-13:00 (日程), 14:00-15:00 (会议)
    # 用户2: 11:00-12:00 (日程), 14:00-15:00 (会议)
    # 共同忙碌时间段合并后为: [09:00-09:30], [11:00-13:00], [14:00-15:00]

    # 预期的共同空闲时间段应为：
    # [09:30-11:00], [13:00-14:00], [15:00-17:00]

    available_times, message = find_meeting_times(
        participants, key_participants, duration, start_date_str, end_date_str
    )
    
    assert "查找成功" in message
    assert "2025-06-27" in available_times
    
    day_slots = available_times["2025-06-27"]
    
    # 验证是否找到了正确的空闲时间段
    # (注意: 时间以ISO格式返回)
    expected_starts = ["09:30", "13:00", "15:00"]
    actual_starts = [datetime.fromisoformat(slot["start_time"]).strftime("%H:%M") for slot in day_slots]
    
    for start in expected_starts:
        assert start in actual_starts
