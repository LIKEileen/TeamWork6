import pytest
import pandas as pd
from unittest.mock import MagicMock
from app.services.schedule_service import (
    get_user_schedule_list,
    add_single_schedule_event,
    add_recurring_schedule_event,
    remove_schedule_event,
    check_schedule_conflict,
    import_excel_schedule,
)
from app.models.schedule import get_user_schedules

# 所有测试函数都将使用 conftest.py 中定义的 fixtures

def test_get_user_schedule_list_service(setup_databases, authed_token):
    """测试获取用户日程列表的服务。"""
    # 用户1在 conftest 中预置了2个日程
    schedules, message = get_user_schedule_list(authed_token)
    assert "success" in message
    assert schedules is not None
    assert len(schedules) == 2

    # 测试使用无效token
    schedules_fail, message_fail = get_user_schedule_list("invalid.token")
    assert schedules_fail is None
    assert "无效" in message_fail


def test_add_single_schedule_event_service(setup_databases, authed_token):
    """测试添加单个日程事件的服务，包括验证逻辑。"""
    # 场景1: 成功添加
    event, message = add_single_schedule_event(
        authed_token, "Team Meeting", "2025-08-01", "10:00", "11:00"
    )
    assert "创建成功" in message
    assert event is not None
    assert event['title'] == "Team Meeting"

    # 场景2: 输入验证失败 - 标题太长
    long_title = "a" * 101
    event_fail, message_fail = add_single_schedule_event(
        authed_token, long_title, "2025-08-01", "14:00", "15:00"
    )
    assert event_fail is None
    assert "事件名称长度不能超过100个字符" in message_fail

    # 场景3: 输入验证失败 - 结束时间早于开始时间
    event_fail, message_fail = add_single_schedule_event(
        authed_token, "Invalid Time", "2025-08-01", "16:00", "15:00"
    )
    assert event_fail is None
    assert "结束时间必须晚于开始时间" in message_fail


def test_remove_schedule_event_service(setup_databases, authed_token):
    """测试删除日程事件的服务。"""
    # conftest 中，ID为1的日程属于用户1
    event_id_to_delete = 1

    # 场景1: 成功删除
    success, message = remove_schedule_event(authed_token, event_id_to_delete)
    assert success is True
    assert "删除成功" in message

    # 验证事件确实已被删除
    schedules_after_delete, _ = get_user_schedule_list(authed_token)
    assert not any(s['id'] == event_id_to_delete for s in schedules_after_delete)

    # 场景2: 删除一个不存在的事件
    success_fail, message_fail = remove_schedule_event(authed_token, 999)
    assert success_fail is False
    assert "事件不存在或无权限删除" in message_fail


def test_add_recurring_schedule_event_service(setup_databases, authed_token, mocker):
    """测试添加重复日程事件的服务。"""
    # 使用mocker来固定_generate_recurring_events_with_conflict_check中的today
    fixed_today = datetime.date(2025, 6, 27)
    mocker.patch('app.models.schedule.datetime.date', type('FixedDate', (datetime.date,), {'today': staticmethod(lambda: fixed_today)}))
    
    # 场景1: 成功添加每日重复事件
    success, message = add_recurring_schedule_event(
        token=authed_token,
        title="Daily Standup",
        start="08:00",
        end="08:15",
        frequency="daily",
        repeat_count=3
    )
    assert success is True
    assert "成功创建3个重复事件" in message

    # 验证数据库中是否真的创建了3个事件
    schedules = get_user_schedules(1) # 用户1
    daily_events = [s for s in schedules if s['title'] == 'Daily Standup']
    assert len(daily_events) == 3


def test_import_excel_schedule_service(setup_databases, authed_token, mocker):
    """
    测试从Excel导入日程的服务。
    我们将模拟文件系统和pandas库的行为。
    """
    # 1. 创建一个模拟的 DataFrame
    mock_data = {
        '标题': ['Excel Event 1', 'Excel Event 2'],
        '日期': ['2025-10-10', '2025-10-11'],
        '开始时间': ['10:00', '14:00'],
        '结束时间': ['11:00', '15:30'],
        '颜色': ['#ff0000', None]
    }
    mock_df = pd.DataFrame(mock_data)

    # 2. 模拟 `pandas.read_excel` 函数，使其返回我们的模拟 DataFrame
    mocker.patch('pandas.read_excel', return_value=mock_df)
    
    # 3. 模拟 `os.remove` 以避免测试尝试删除一个不存在的文件
    mock_remove = mocker.patch('os.remove')

    # 4. 调用服务函数
    # 文件路径可以是任意的，因为它被mock了
    success, message = import_excel_schedule(authed_token, "dummy/path/to/file.xlsx")

    # 5. 验证结果
    assert success is True
    assert "导入完成：成功2条" in message
    mock_remove.assert_called_once_with("dummy/path/to/file.xlsx")

    # 验证事件是否已添加到数据库
    schedules, _ = get_user_schedule_list(authed_token, start_date='2025-10-01', end_date='2025-10-31')
    assert len(schedules) == 2
    titles = {s['title'] for s in schedules}
    assert 'Excel Event 1' in titles
    assert 'Excel Event 2' in titles


def test_import_excel_missing_columns(setup_databases, authed_token, mocker):
    """测试导入的Excel缺少必要列时的失败场景。"""
    # 创建一个缺少 '日期' 列的模拟 DataFrame
    mock_data = {'标题': ['Event 1'], '开始时间': ['10:00'], '结束时间': ['11:00']}
    mock_df = pd.DataFrame(mock_data)
    mocker.patch('pandas.read_excel', return_value=mock_df)
    mocker.patch('os.remove')

    success, message = import_excel_schedule(authed_token, "dummy/path/to/file.xlsx")
    
    assert success is False
    assert "Excel文件缺少必需的列: 日期" in message
