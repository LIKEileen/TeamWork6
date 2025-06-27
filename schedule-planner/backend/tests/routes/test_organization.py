import pytest
import json

def test_create_organization_success(test_client, outsider_token):
    """测试成功创建一个新组织。"""
    response = test_client.post('/org', json={
        "token": outsider_token,
        "name": "The Outsiders Club",
        "members": [2, 3] # 添加已存在的用户作为初始成员
    })
    data = response.get_json()

    assert response.status_code == 200
    assert data['code'] == 1
    assert "组织创建成功" in data['message']
    new_org_id = data['data']['id']
    
    # 验证新组织
    get_response = test_client.get(f'/org/{new_org_id}', json={"token": outsider_token})
    get_data = get_response.get_json()
    assert get_response.status_code == 200
    assert len(get_data['data']['members']) == 3 # 创建者 + 2个初始成员


def test_get_organization_details(test_client, creator_token):
    """测试成功获取组织详情。"""
    response = test_client.get('/org/org_1', json={"token": creator_token})
    data = response.get_json()

    assert response.status_code == 200
    assert data['code'] == 1
    assert data['data']['name'] == 'Test Org One'
    assert len(data['data']['members']) == 3


def test_update_organization_name_permission_denied(test_client, member_token):
    """测试普通成员更新组织名称失败（权限不足）。"""
    response = test_client.put('/org/org_1', json={
        "token": member_token,
        "name": "New Name By Member"
    })
    data = response.get_json()

    assert response.status_code == 400
    assert data['code'] == 0
    assert "权限不足" in data['message']


def test_update_organization_name_success(test_client, creator_token):
    """测试创建者成功更新组织名称。"""
    response = test_client.put('/org/org_1', json={
        "token": creator_token,
        "name": "Test Org One Renamed"
    })
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['code'] == 1
    assert "组织名称已更新" in data['message']


def test_delete_organization_permission_denied(test_client, admin_token):
    """测试管理员删除组织失败（权限不足）。"""
    response = test_client.delete('/org/org_1', json={"token": admin_token})
    data = response.get_json()

    assert response.status_code == 400
    assert data['code'] == 0
    assert "只有创建者可以删除组织" in data['message']


def test_delete_organization_success(test_client, creator_token):
    """测试创建者成功删除组织。"""
    response = test_client.delete('/org/org_1', json={"token": creator_token})
    data = response.get_json()

    assert response.status_code == 200
    assert data['code'] == 1
    assert "组织已删除" in data['message']

    # 验证组织已不存在
    get_response = test_client.get('/org/org_1', json={"token": creator_token})
    assert get_response.status_code == 404


def test_set_admins_flow(test_client, creator_token):
    """测试设置管理员的完整流程。"""
    # 初始状态：user 2 是 admin, user 3 是 member
    # 目标：将 user 3 提升为 admin, user 2 降级为 member
    response = test_client.post('/org/org_1/admins', json={
        "token": creator_token,
        "adminIds": [3] # 将user 3设为唯一管理员
    })
    data = response.get_json()

    assert response.status_code == 200
    assert data['code'] == 1
    assert "成功设置 1 名管理员" in data['message']

    # 验证角色变更
    details_response = test_client.get('/org/org_1', json={"token": creator_token})
    details_data = details_response.get_json()
    member_roles = {member['id']: member['role'] for member in details_data['data']['members']}
    
    assert member_roles['1'] == 'creator'
    assert member_roles['2'] == '' # 被降级
    assert member_roles['3'] == 'admin' # 被提升


def test_join_request_flow(test_client, outsider_token, creator_token):
    """测试申请加入组织的完整流程。"""
    # 1. 组织外成员(user 4)申请加入 org_1
    join_res = test_client.post('/org/join-request', json={
        "token": outsider_token,
        "orgId": "org_1",
        "message": "Please let me join!"
    })
    assert join_res.status_code == 200
    assert join_res.get_json()['code'] == 1

    # 2. 创建者获取申请列表
    list_res = test_client.get('/org/org_1/join-requests', json={"token": creator_token})
    list_data = list_res.get_json()
    assert list_res.status_code == 200
    assert len(list_data['data']) == 1
    request_id = list_data['data'][0]['id']

    # 3. 创建者接受申请
    handle_res = test_client.post(f'/org/join-request/{request_id}/accept', json={"token": creator_token})
    assert handle_res.status_code == 200
    assert handle_res.get_json()['code'] == 1

    # 4. 验证新成员已加入
    details_res = test_client.get('/org/org_1', json={"token": creator_token})
    details_data = details_res.get_json()
    assert len(details_data['data']['members']) == 4 # 原有3名 + 新加入1名


def test_search_users(test_client, creator_token):
    """测试用户搜索接口。"""
    # 搜索 'Admin' 应该能找到用户 'Admin_Two'
    response = test_client.get('/users/search?q=Admin', json={"token": creator_token})
    data = response.get_json()

    assert response.status_code == 200
    assert data['code'] == 1
    assert len(data['data']) > 0
    assert any(user['name'] == 'Admin_Two' for user in data['data'])
