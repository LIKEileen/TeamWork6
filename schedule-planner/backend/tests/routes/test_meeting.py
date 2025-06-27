import pytest
import json
from datetime import datetime, timedelta

def test_get_meeting_list_success(test_client, authed_token):
    """
    测试成功获取用户的会议列表。
    """
    response = test_client.post('/meeting/list', json={
        "token": authed_token
    })
    data = response.get_json()

    assert response.status_code == 200
    assert data['code'] == 1
    # 用户1参与了 'Past Meeting'
    assert len(data['data']['meetings']) > 0
    assert any(m['title'] == 'Past Meeting' for m in data['data']['meetings'])

def test_get_meeting_list_with_date_filter(test_client, authed_token):
    """
    测试使用日期范围过滤会议列表。
    """
    response = test_client.post('/meeting/list', json={
        "token": authed_token,
        "start_date": "2025-01-01",
        "end_date": "2025-01-31"
    })
    data = response.get_json()

    assert response.status_code == 200
    assert data['code'] == 1
    # 用户1在1月份只有一个会议
    assert len(data['data']['meetings']) == 1
    assert data['data']['meetings'][0]['title'] == 'Past Meeting'

def test_get_meeting_list_invalid_token(test_client):
    """
    测试使用无效token获取会议列表。
    """
    response = test_client.post('/meeting/list', json={
        "token": "a.fake.token"
    })
    data = response.get_json()
    assert response.status_code == 401
    assert data['code'] == 0
    assert "token 无效" in data['message']


def test_create_meeting_success(test_client, authed_token):
    """
    测试成功创建一个新会议。
    """
    start_time = (datetime.utcnow() + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (datetime.utcnow() + timedelta(days=5, hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    
    response = test_client.post('/meeting/create', json={
        "token": authed_token,
        "title": "New Team Sync",
        "description": "Weekly sync meeting.",
        "start_time": start_time,
        "end_time": end_time,
        "participants": [1, 2], # 包含创建者1和成员2
        "key_participants": [1]
    })
    data = response.get_json()

    assert response.status_code == 200
    assert data['code'] == 1
    assert "会议创建成功" in data['message']
    assert data['data']['title'] == "New Team Sync"
    assert data['data']['creator_id'] == 1 # 登录用户是1


def test_create_meeting_missing_fields(test_client, authed_token):
    """
    测试创建会议时缺少必要字段。
    """
    response = test_client.post('/meeting/create', json={
        "token": authed_token,
        # 缺少 'title'
        "start_time": "2025-09-01 10:00:00",
        "end_time": "2025-09-01 11:00:00",
        "participants": [1, 2]
    })
    data = response.get_json()
    assert response.status_code == 400
    assert data['code'] == 0
    assert "缺少必填字段: title" in data['message']


def test_find_available_time(test_client, authed_token, mocker):
    """
    测试查找可用会议时间接口。
    我们将模拟(mock)底层的 find_meeting_times 服务，以专注于测试路由逻辑。
    """
    # 模拟 find_meeting_times 函数的返回值
    mock_return_value = (
        ["2025-09-01 14:00:00", "2025-09-01 15:00:00"],
        "成功找到2个可用时间段"
    )
    mocker.patch('app.routes.meeting.find_meeting_times', return_value=mock_return_value)

    response = test_client.post('/meeting/find-time', json={
        "token": authed_token,
        "participants": [1, 2],
        "duration": 60,
        "start_date": "2025-09-01",
        "end_date": "2025-09-01"
    })
    data = response.get_json()

    assert response.status_code == 200
    assert data['code'] == 1
    assert "成功找到2个可用时间段" in data['message']
    assert len(data['data']['available_times']) == 2
    assert "2025-09-01 14:00:00" in data['data']['available_times']
