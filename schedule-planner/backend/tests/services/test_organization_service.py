import pytest
from app.services.organization_service import (
    create_organization_service,
    get_organization_service,
    update_organization_service,
    delete_organization_service,
    set_admins_service,
    join_request_service,
    get_join_requests_service,
    handle_join_request_service,
    invite_user_service,
    get_invitations_service,
    handle_invitation_service,
    search_users_service,
)

# --- Organization Management ---

def test_create_organization_service_success(setup_databases, outsider_token):
    """测试成功创建一个组织。"""
    org_details, message = create_organization_service(outsider_token, "The Newbies", member_ids=[1, 2])
    
    assert "组织创建成功" in message
    assert org_details is not None
    assert org_details['name'] == "The Newbies"
    # 创建者(user 4) + 2个初始成员
    assert len(org_details['members']) == 3


def test_create_organization_service_invalid_name(setup_databases, creator_token):
    """测试因组织名称无效而创建失败。"""
    org_details, message = create_organization_service(creator_token, "A") # 名称太短
    assert org_details is None
    assert "组织名称长度应为2-20个字符" in message


def test_get_organization_service(setup_databases, admin_token):
    """测试获取组织详情服务。"""
    # 管理员(user 2)是 org_1 的成员
    org_details, message = get_organization_service(admin_token, 'org_1')
    assert "success" in message
    assert org_details is not None
    assert org_details['name'] == 'Test Org One'


def test_delete_organization_service_permission(setup_databases, admin_token, creator_token):
    """测试删除组织服务的权限。"""
    # 管理员(user 2)尝试删除，应失败
    success, message = delete_organization_service(admin_token, 'org_1')
    assert not success
    assert "只有创建者可以删除组织" in message
    
    # 创建者(user 1)尝试删除，应成功
    success, message = delete_organization_service(creator_token, 'org_1')
    assert success
    assert "组织已删除" in message


# --- Membership and Roles ---

def test_set_admins_service_success(setup_databases, creator_token):
    """测试创建者成功设置管理员。"""
    # 将普通成员(user 3)提升为管理员
    success, message = set_admins_service(creator_token, 'org_1', ['3'])
    assert success
    assert "成功设置 1 名管理员" in message

    # 验证角色变更
    org_details, _ = get_organization_service(creator_token, 'org_1')
    member_roles = {member['id']: member['role'] for member in org_details['members']}
    assert member_roles['3'] == 'admin'


def test_set_admins_service_permission_denied(setup_databases, admin_token):
    """测试非创建者设置管理员失败。"""
    success, message = set_admins_service(admin_token, 'org_1', ['3'])
    assert not success
    assert "只有创建者可以设置管理员" in message

# --- Join Requests ---

def test_join_request_service_flow(setup_databases, outsider_token, creator_token):
    """测试完整的加入申请流程。"""
    # 1. 组织外成员(user 4)发送加入请求
    success, message = join_request_service(outsider_token, 'org_1', "I'm a great developer!")
    assert success
    assert "申请已提交" in message

    # 2. 创建者获取申请列表
    requests, message = get_join_requests_service(creator_token, 'org_1')
    assert "success" in message
    assert len(requests) == 1
    request_id = requests[0]['id']
    assert requests[0]['userId'] == '4'

    # 3. 创建者接受请求
    success, message = handle_join_request_service(creator_token, request_id, 'accept')
    assert success
    assert "申请已通过" in message
    
    # 4. 验证新成员已加入
    org_details, _ = get_organization_service(creator_token, 'org_1')
    assert len(org_details['members']) == 4 # 原有3名 + 新增1名

# --- Invitations ---

def test_invitation_service_flow(setup_databases, admin_token, outsider_token):
    """测试完整的邀请流程。"""
    # 1. 管理员(user 2)邀请组织外成员(user 4)
    success, message = invite_user_service(admin_token, 'org_1', 4)
    assert success
    assert "邀请已发送" in message

    # 2. 被邀请者(user 4)获取他的邀请列表
    invitations, message = get_invitations_service(outsider_token)
    assert "success" in message
    assert len(invitations) == 1
    invitation_id = invitations[0]['id']
    assert invitations[0]['orgName'] == 'Test Org One'

    # 3. 被邀请者接受邀请
    success, message = handle_invitation_service(outsider_token, invitation_id, 'accept')
    assert success
    assert "已加入组织" in message
    
    # 4. 验证新成员已加入
    org_details, _ = get_organization_service(admin_token, 'org_1')
    assert len(org_details['members']) == 4

# --- User Search ---

def test_search_users_service(setup_databases, member_token):
    """测试用户搜索服务。"""
    # 搜索 "Admin" 应该能找到 'Admin_Two'
    users, message = search_users_service(member_token, 'Admin')
    assert "success" in message
    assert len(users) >= 1
    assert any(user['name'] == 'Admin_Two' for user in users)

    # 搜索关键词太短
    users_fail, message_fail = search_users_service(member_token, '')
    assert "搜索关键词不能为空" in message_fail
    assert users_fail == []
