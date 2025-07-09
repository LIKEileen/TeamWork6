# Author: 唐震
from ..models.organization import (
    create_organization, get_organization_details, update_organization_name,
    delete_organization, set_organization_admins, search_organization,
    create_join_request, create_invitation, get_user_invitations,
    handle_invitation, search_users, get_organization_join_requests,
    handle_join_request, get_user_organizations
)
from ..services.auth_service import verify_token

def create_organization_service(token, name, member_ids=None):
    """创建组织服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证组织名称
    if not name or len(name.strip()) < 2 or len(name.strip()) > 20:
        return None, "组织名称长度应为2-20个字符"
    
    # 创建组织
    org_id, message = create_organization(user_id, name.strip(), member_ids)
    
    if org_id:
        # 获取创建后的组织详情
        org_details, _ = get_organization_details(org_id)
        return org_details, message
    
    return None, message

def get_organization_service(token, org_id):
    """获取组织详情服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    return get_organization_details(org_id)

def update_organization_service(token, org_id, new_name):
    """更新组织名称服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证组织名称
    if not new_name or len(new_name.strip()) < 2 or len(new_name.strip()) > 20:
        return False, "组织名称长度应为2-20个字符"
    
    return update_organization_name(org_id, user_id, new_name.strip())

def delete_organization_service(token, org_id):
    """删除组织服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    return delete_organization(org_id, user_id)

def set_admins_service(token, org_id, admin_ids):
    """设置管理员服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证管理员ID列表
    if not isinstance(admin_ids, list):
        return False, "管理员ID必须是数组"
    
    # 验证每个管理员ID
    if len(admin_ids) > 5:
        return False, "最多只能设置5名管理员"
    
    # 去重处理
    unique_admin_ids = list(set(admin_ids))
    if len(unique_admin_ids) != len(admin_ids):
        return False, "管理员列表中存在重复用户"
    
    # 验证每个ID不为空
    for admin_id in unique_admin_ids:
        if not admin_id or str(admin_id).strip() == '':
            return False, "管理员ID不能为空"
    
    return set_organization_admins(org_id, user_id, unique_admin_ids)

def search_organization_service(token, org_id):
    """搜索组织服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    return search_organization(org_id)

def join_request_service(token, org_id, message=""):
    """申请加入组织服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    return create_join_request(org_id, user_id, message)

def get_join_requests_service(token, org_id):
    """获取组织加入申请列表服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return [], "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    return get_organization_join_requests(org_id, user_id)

def handle_join_request_service(token, request_id, action):
    """处理加入申请服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证操作类型
    if action not in ['accept', 'reject']:
        return False, "无效的操作类型"
    
    return handle_join_request(request_id, user_id, action)

def invite_user_service(token, org_id, invitee_id):
    """邀请用户服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    return create_invitation(org_id, user_id, invitee_id)

def get_invitations_service(token):
    """获取邀请列表服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return [], "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    return get_user_invitations(user_id)

def handle_invitation_service(token, invitation_id, action):
    """处理邀请服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证操作类型
    if action not in ['accept', 'reject']:
        return False, "无效的操作类型"
    
    return handle_invitation(invitation_id, user_id, action)

def search_users_service(token, query):
    """搜索用户服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return [], "用户未登录或 token 无效"
    
    # 验证查询关键词
    if not query or len(query.strip()) < 1:
        return [], "搜索关键词不能为空"
    
    return search_users(query.strip())

def get_user_organizations_service(token):
    """获取用户组织列表服务"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return [], "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    return get_user_organizations(user_id)