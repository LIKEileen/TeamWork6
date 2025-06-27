import pytest
import datetime
from app.models.schedule import (
    get_user_schedules,
    check_time_conflict,
    create_schedule_event,
    delete_schedule_event,
    create_recurring_event,
)

# 所有测试函数都将使用 setup_databases fixture
def test_get_user_schedules(setup_databases):
    """测试获取用户日程列表的功能。"""
    # 场景1: 获取用户1的所有日程 (应有3个)
    user1_events = get_user_schedules(user_id=1)
    assert len(user1_events) == 3

    # 场景2: 按日期范围获取用户1的日程
    start_date = datetime.date(2025, 6, 27)
    end_date = datetime.date(2025, 6, 27)
    user1_events_today = get_user_schedules(1, start_date, end_date)
    assert len(user1_events_today) == 2
    titles = {event['title'] for event in user1_events_today}
    assert "Morning Standup" in titles
    assert "Lunch with Team" in titles
    
    # 场景3: 获取一个没有日程的用户
    user3_events = get_user_schedules(user_id=3)
    assert len(user3_events) == 0


def test_check_time_conflict(setup_databases):
    """全面测试时间冲突检测逻辑。"""
    user_id = 1
    conflict_day = '2025-06-28' # 虚拟数据中已存在 10:00-12:00 的事件

    # 场景1: 完全不冲突 (之前)
    no_conflict_before = check_time_conflict(user_id, conflict_day, '08:00', '09:00')
    assert len(no_conflict_before) == 0

    # 场景2: 完全不冲突 (之后)
    no_conflict_after = check_time_conflict(user_id, conflict_day, '12:00', '13:00')
    assert len(no_conflict_after) == 0

    # 场景3: 冲突 - 新事件与现有事件完全重合
    conflict_exact = check_time_conflict(user_id, conflict_day, '10:00', '12:00')
    assert len(conflict_exact) == 1
    assert conflict_exact[0]['title'] == 'Conflict Base Event'

    # 场景4: 冲突 - 新事件开始时间与现有事件重叠
    conflict_overlap_start = check_time_conflict(user_id, conflict_day, '09:30', '10:30')
    assert len(conflict_overlap_start) == 1

    # 场景5: 冲突 - 新事件结束时间与现有事件重叠
    conflict_overlap_end = check_time_conflict(user_id, conflict_day, '11:30', '12:30')
    assert len(conflict_overlap_end) == 1
    
    # 场景6: 冲突 - 新事件被现有事件完全包含
    conflict_contained = check_time_conflict(user_id, conflict_day, '10:30', '11:30')
    assert len(conflict_contained) == 1

    # 场景7: 冲突 - 新事件完全包含现有事件
    conflict_contains = check_time_conflict(user_id, conflict_day, '09:00', '13:00')
    assert len(conflict_contains) == 1

    # 场景8: 测试排除ID的功能 (当更新事件时)
    # 假设我们正在更新ID为3的事件 ('Conflict Base Event')
    no_conflict_when_excluded = check_time_conflict(user_id, conflict_day, '10:15', '11:45', exclude_event_id=3)
    assert len(no_conflict_when_excluded) == 0


def test_create_schedule_event(setup_databases):
    """测试创建日程事件，包括成功、冲突和强制创建。"""
    user_id = 2
    day = '2025-06-27'

    # 场景1: 成功创建不冲突的事件
    event, message = create_schedule_event(user_id, "Afternoon Coffee", day, '15:00', '15:30')
    assert "创建成功" in message
    assert event is not None
    assert event['title'] == 'Afternoon Coffee'

    # 场景2: 因时间冲突导致创建失败
    # 虚拟数据中用户2已有 11:00-12:00 的事件
    event_fail, message_fail = create_schedule_event(user_id, "Failed Event", day, '11:30', '12:30')
    assert event_fail is None
    assert "时间冲突" in message_fail
    assert "Project Sync" in message_fail # 检查是否返回了冲突的事件名

    # 场景3: 强制创建，忽略冲突
    event_force, message_force = create_schedule_event(user_id, "Forced Event", day, '11:45', '12:15', force_create=True)
    assert "创建成功" in message_force
    assert event_force is not None

def test_delete_schedule_event(setup_databases):
    """测试删除日程事件的权限和功能。"""
    user_id_owner = 1
    user_id_other = 2
    event_id_to_delete = 1 # 'Morning Standup', 属于用户1

    # 场景1: 其他用户尝试删除，应失败
    success, message = delete_schedule_event(user_id_other, event_id_to_delete)
    assert not success
    assert "事件不存在或无权限删除" in message

    # 场景2: 事件所有者删除，应成功
    success, message = delete_schedule_event(user_id_owner, event_id_to_delete)
    assert success
    assert "删除成功" in message

    # 验证事件已被删除
    cursor = setup_databases["main_db"].cursor()
    cursor.execute("SELECT 1 FROM schedule_events WHERE id = ?", (event_id_to_delete,))
    assert cursor.fetchone() is None


def test_create_recurring_event(setup_databases):
    """测试创建长期重复事件。"""
    user_id = 3
    # 在conftest.py中，日期是硬编码的，所以这里的today也应该是
    # 但为了测试的健壮性，我们最好不要依赖于运行测试时的真实日期
    # _generate_recurring_events_with_conflict_check 内部会使用 datetime.date.today()
    # 我们可以通过 monkeypatch 来固定这个日期
    fixed_today = datetime.date(2025, 6, 27)
    pytest.MonkeyPatch().setattr('app.models.schedule.datetime.date', type('FixedDate', (datetime.date,), {'today': staticmethod(lambda: fixed_today)}))


    # 场景1: 创建一个每日重复5次的事件
    success, message = create_recurring_event(
        user_id, "Daily Scrum", "09:00", "09:15", "daily", repeat_count=5
    )
    assert success
    assert "成功创建5个重复事件" in message

    # 验证数据库中是否生成了5个事件
    events = get_user_schedules(user_id, fixed_today, fixed_today + datetime.timedelta(days=4))
    assert len(events) == 5
    assert events[0]['day'] == '2025-06-27'
    assert events[4]['day'] == '2025-07-01'

    # 场景2: 创建自定义日期的事件
    custom_dates = ['2025-08-01', '2025-08-08', '2025-08-15']
    success, message = create_recurring_event(
        user_id, "Custom Fridays", "16:00", "17:00", "custom", custom_dates=custom_dates
    )
    assert success
    assert "成功创建3个重复事件" in message
    events_custom = get_user_schedules(user_id, datetime.date(2025, 8, 1), datetime.date(2025, 8, 31))
    assert len(events_custom) == 3
