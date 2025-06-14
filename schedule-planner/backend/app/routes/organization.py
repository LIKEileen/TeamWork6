# Author: 唐震
from flask import Blueprint, request, jsonify
from ..services.organization_service import (
    create_organization_service, get_organization_service, update_organization_service,
    delete_organization_service, set_admins_service, search_organization_service,
    join_request_service, invite_user_service, get_invitations_service,
    handle_invitation_service, search_users_service, get_join_requests_service,
    handle_join_request_service
)
import logging

organization_bp = Blueprint('organization', __name__)

def validate_request_data(data, required_fields):
    """验证请求数据"""
    if not data:
        return False, "请求数据不能为空"
    
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"缺少必填字段: {field}"
        if isinstance(data[field], str) and not data[field].strip():
            return False, f"字段不能为空: {field}"
    
    return True, "验证通过"

@organization_bp.route('/org/<org_id>', methods=['GET'])
def get_organization_details(org_id):
    """获取组织详情"""
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        
        # 获取组织详情
        org_details, message = get_organization_service(token, org_id)
        
        if org_details:
            return jsonify({
                'code': 1,
                'message': message,
                'data': org_details
            })
        else:
            return jsonify({
                'code': 0,
                'message': message
            }), 404 if message == "组织不存在" else 401
            
    except Exception as e:
        logging.error(f"Get organization details error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@organization_bp.route('/org', methods=['POST'])
def create_organization():
    """创建组织"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'name'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        name = data.get('name')
        members = data.get('members', [])
        
        # 创建组织
        org_details, message = create_organization_service(token, name, members)
        
        if org_details:
            return jsonify({
                'code': 1,
                'message': message,
                'data': org_details
            })
        else:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
            
    except Exception as e:
        logging.error(f"Create organization error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@organization_bp.route('/org/<org_id>', methods=['PUT'])
def update_organization(org_id):
    """更新组织名称"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'name'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        token = data.get('token')
        name = data.get('name')
        
        # 更新组织名称
        success, message = update_organization_service(token, org_id, name)
        
        return jsonify({
            'code': 1 if success else 0,
            'message': message,
            'success': success
        }), 200 if success else 400
            
    except Exception as e:
        logging.error(f"Update organization error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'success': False
        }), 500

@organization_bp.route('/org/<org_id>', methods=['DELETE'])
def delete_organization(org_id):
    """删除组织"""
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'success': False
            }), 400
        
        token = data.get('token')
        
        # 删除组织
        success, message = delete_organization_service(token, org_id)
        
        return jsonify({
            'code': 1 if success else 0,
            'message': message,
            'success': success
        }), 200 if success else 400
            
    except Exception as e:
        logging.error(f"Delete organization error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'success': False
        }), 500

@organization_bp.route('/org/<org_id>/admins', methods=['POST'])
def set_organization_admins(org_id):
    """设置组织管理员"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'adminIds'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'success': False
            }), 400
        
        token = data.get('token')
        admin_ids = data.get('adminIds')
        
        # 设置管理员
        success, message = set_admins_service(token, org_id, admin_ids)
        
        return jsonify({
            'code': 1 if success else 0,
            'message': message,
            'success': success
        }), 200 if success else 400
            
    except Exception as e:
        logging.error(f"Set organization admins error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'success': False
        }), 500

@organization_bp.route('/org/search', methods=['GET'])
def search_organization():
    """搜索组织"""
    try:
        data = request.get_json() or {}
        org_id = request.args.get('id')
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message
            }), 400
        
        if not org_id:
            return jsonify({
                'code': 0,
                'message': '缺少组织ID参数'
            }), 400
        
        token = data.get('token')
        
        # 搜索组织
        org_details, message = search_organization_service(token, org_id)
        
        return jsonify({
            'code': 1,
            'message': message,
            'data': org_details
        })
            
    except Exception as e:
        logging.error(f"Search organization error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误'
        }), 500

@organization_bp.route('/org/join-request', methods=['POST'])
def join_organization_request():
    """申请加入组织"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'orgId'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'success': False
            }), 400
        
        token = data.get('token')
        org_id = data.get('orgId')
        message_text = data.get('message', '')
        
        # 申请加入组织
        success, message = join_request_service(token, org_id, message_text)
        
        return jsonify({
            'code': 1 if success else 0,
            'message': message,
            'success': success
        }), 200 if success else 400
            
    except Exception as e:
        logging.error(f"Join organization request error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'success': False
        }), 500

@organization_bp.route('/org/<org_id>/join-requests', methods=['GET'])
def get_organization_join_requests(org_id):
    """获取组织的加入申请列表"""
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': []
            }), 400
        
        token = data.get('token')
        
        # 获取申请列表
        requests, message = get_join_requests_service(token, org_id)
        
        return jsonify({
            'code': 1,
            'message': message,
            'data': requests
        })
            
    except Exception as e:
        logging.error(f"Get organization join requests error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': []
        }), 500

@organization_bp.route('/org/join-request/<request_id>/<action>', methods=['POST'])
def handle_join_request(request_id, action):
    """处理加入申请"""
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'success': False
            }), 400
        
        token = data.get('token')
        
        # 处理申请
        success, message = handle_join_request_service(token, request_id, action)
        
        return jsonify({
            'code': 1 if success else 0,
            'message': message,
            'success': success
        }), 200 if success else 400
            
    except Exception as e:
        logging.error(f"Handle join request error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'success': False
        }), 500

@organization_bp.route('/users/search', methods=['GET'])
def search_users():
    """搜索用户"""
    try:
        data = request.get_json() or {}
        query = request.args.get('q')
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': []
            }), 400
        
        if not query:
            return jsonify({
                'code': 0,
                'message': '缺少搜索关键词',
                'data': []
            }), 400
        
        token = data.get('token')
        
        # 搜索用户
        users, message = search_users_service(token, query)
        
        return jsonify({
            'code': 1,
            'message': message,
            'data': users
        })
            
    except Exception as e:
        logging.error(f"Search users error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': []
        }), 500

@organization_bp.route('/org/<org_id>/invite', methods=['POST'])
def invite_user_to_organization(org_id):
    """邀请用户加入组织"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token', 'userId'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'success': False
            }), 400
        
        token = data.get('token')
        user_id = data.get('userId')
        
        # 邀请用户
        success, message = invite_user_service(token, org_id, user_id)
        
        return jsonify({
            'code': 1 if success else 0,
            'message': message,
            'success': success
        }), 200 if success else 400
            
    except Exception as e:
        logging.error(f"Invite user to organization error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'success': False
        }), 500

@organization_bp.route('/user/invitations', methods=['GET'])
def get_user_invitations():
    """获取用户收到的邀请"""
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'data': []
            }), 400
        
        token = data.get('token')
        
        # 获取邀请列表
        invitations, message = get_invitations_service(token)
        
        return jsonify({
            'code': 1,
            'message': message,
            'data': invitations
        })
            
    except Exception as e:
        logging.error(f"Get user invitations error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'data': []
        }), 500

@organization_bp.route('/invitation/<invitation_id>/<action>', methods=['POST'])
def handle_invitation(invitation_id, action):
    """处理组织邀请"""
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        valid, message = validate_request_data(data, ['token'])
        if not valid:
            return jsonify({
                'code': 0,
                'message': message,
                'success': False
            }), 400
        
        token = data.get('token')
        
        # 处理邀请
        success, message = handle_invitation_service(token, invitation_id, action)
        
        return jsonify({
            'code': 1 if success else 0,
            'message': message,
            'success': success
        }), 200 if success else 400
            
    except Exception as e:
        logging.error(f"Handle invitation error: {str(e)}")
        return jsonify({
            'code': 0,
            'message': '服务器内部错误',
            'success': False
        }), 500