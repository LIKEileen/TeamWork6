# Author: 唐震
import sqlite3
import os
from datetime import datetime
import uuid

def get_db_connection():
    """获取组织数据库连接"""
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'organization.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_db_connection():
    """获取用户数据库连接"""
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'schedule_planner.db')
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"数据库文件不存在: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_user_id(user_id):
    """标准化用户ID - 统一转换为字符串进行比较"""
    if user_id is None:
        return None
    return str(user_id).strip()

def init_organization_db():
    """初始化组织数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 创建组织表 - creator_id存储为TEXT类型
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                creator_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建组织成员表 - user_id存储为TEXT类型
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organization_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT DEFAULT '',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE,
                UNIQUE(org_id, user_id)
            )
        ''')
        
        # 创建邀请表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                inviter_id TEXT NOT NULL,
                invitee_id TEXT NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建加入申请表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS join_requests (
                id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        print("Organization database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing organization database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def create_organization(creator_id, name, member_ids=None):
    """创建组织"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        org_id = f"org_{str(uuid.uuid4())[:8]}"
        # 标准化creator_id
        creator_id = normalize_user_id(creator_id)
        
        # 创建组织
        cursor.execute('''
            INSERT INTO organizations (id, name, creator_id)
            VALUES (?, ?, ?)
        ''', (org_id, name, creator_id))
        
        # 添加创建者为成员
        cursor.execute('''
            INSERT INTO organization_members (org_id, user_id, role)
            VALUES (?, ?, 'creator')
        ''', (org_id, creator_id))
        
        # 添加其他成员
        if member_ids:
            for member_id in member_ids:
                try:
                    member_id = normalize_user_id(member_id)
                    cursor.execute('''
                        INSERT INTO organization_members (org_id, user_id, role)
                        VALUES (?, ?, '')
                    ''', (org_id, member_id))
                except sqlite3.IntegrityError:
                    # 忽略重复添加
                    pass
        
        conn.commit()
        return org_id, "组织创建成功"
        
    except Exception as e:
        conn.rollback()
        return None, f"创建失败: {str(e)}"
    finally:
        conn.close()

def get_organization_details(org_id):
    """获取组织详情"""
    conn = get_db_connection()
    user_conn = get_user_db_connection()
    cursor = conn.cursor()
    user_cursor = user_conn.cursor()
    
    try:
        # 获取组织基本信息
        cursor.execute('''
            SELECT id, name, creator_id
            FROM organizations
            WHERE id = ?
        ''', (org_id,))
        
        org = cursor.fetchone()
        if not org:
            return None, "组织不存在"
        
        # 获取成员列表
        cursor.execute('''
            SELECT user_id, role, joined_at
            FROM organization_members
            WHERE org_id = ?
            ORDER BY 
                CASE role 
                    WHEN 'creator' THEN 1 
                    WHEN 'admin' THEN 2 
                    ELSE 3 
                END,
                joined_at
        ''', (org_id,))
        
        members = []
        for member in cursor.fetchall():
            # 从用户数据库获取用户信息
            try:
                user_cursor.execute('''
                    SELECT nickname FROM users WHERE CAST(id AS TEXT) = ?
                ''', (normalize_user_id(member['user_id']),))
                user_info = user_cursor.fetchone()
                user_name = user_info['nickname'] if user_info else '未知用户'
            except Exception as e:
                print(f"获取用户信息失败: {e}")
                user_name = f"用户_{member['user_id']}"
            
            members.append({
                'id': member['user_id'],
                'name': user_name,
                'role': member['role'],
                'avatarUrl': None
            })
        
        return {
            'id': org['id'],
            'name': org['name'],
            'members': members
        }, "success"
        
    except Exception as e:
        return None, f"获取失败: {str(e)}"
    finally:
        conn.close()
        user_conn.close()

def update_organization_name(org_id, user_id, new_name):
    """更新组织名称"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        user_id = normalize_user_id(user_id)
        
        # 检查用户权限
        cursor.execute('''
            SELECT role FROM organization_members
            WHERE org_id = ? AND user_id = ?
        ''', (org_id, user_id))
        
        member = cursor.fetchone()
        if not member or member['role'] not in ['creator', 'admin']:
            return False, "权限不足"
        
        # 更新组织名称
        cursor.execute('''
            UPDATE organizations
            SET name = ?
            WHERE id = ?
        ''', (new_name, org_id))
        
        if cursor.rowcount == 0:
            return False, "组织不存在"
        
        conn.commit()
        return True, "组织名称已更新"
        
    except Exception as e:
        conn.rollback()
        return False, f"更新失败: {str(e)}"
    finally:
        conn.close()

def delete_organization(org_id, user_id):
    """删除组织"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        user_id = normalize_user_id(user_id)
        
        # 检查是否为创建者
        cursor.execute('''
            SELECT creator_id FROM organizations
            WHERE id = ?
        ''', (org_id,))
        
        org = cursor.fetchone()
        if not org:
            return False, "组织不存在"
        
        # 标准化比较
        creator_id = normalize_user_id(org['creator_id'])
        if creator_id != user_id:
            return False, f"只有创建者可以删除组织 (创建者ID: {creator_id}, 当前用户ID: {user_id})"
        
        # 删除组织（级联删除成员和邀请）
        cursor.execute('DELETE FROM organizations WHERE id = ?', (org_id,))
        
        conn.commit()
        return True, "组织已删除"
        
    except Exception as e:
        conn.rollback()
        return False, f"删除失败: {str(e)}"
    finally:
        conn.close()

def set_organization_admins(org_id, user_id, admin_ids):
    """设置组织管理员"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        user_id = normalize_user_id(user_id)
        
        # 检查是否为创建者
        cursor.execute('''
            SELECT creator_id FROM organizations
            WHERE id = ?
        ''', (org_id,))
        
        org = cursor.fetchone()
        if not org:
            return False, "组织不存在"
        
        # 标准化比较
        creator_id = normalize_user_id(org['creator_id'])
        
        if creator_id != user_id:
            return False, f"只有创建者可以设置管理员"
        
        if len(admin_ids) > 5:
            return False, "最多只能设置5名管理员"
        
        # 验证每个要设置为管理员的用户
        invalid_users = []
        valid_admin_ids = []
        
        for admin_id in admin_ids:
            admin_id = normalize_user_id(admin_id)
            
            # 检查用户是否是创建者
            if admin_id == creator_id:
                invalid_users.append(f"用户{admin_id}: 创建者不能被设置为管理员")
                continue
            
            # 检查用户是否是组织成员
            cursor.execute('''
                SELECT 1 FROM organization_members
                WHERE org_id = ? AND user_id = ?
            ''', (org_id, admin_id))
            
            if not cursor.fetchone():
                invalid_users.append(f"用户{admin_id}: 不是组织成员")
                continue
            
            valid_admin_ids.append(admin_id)
        
        # 如果有无效用户，返回错误信息
        if invalid_users:
            error_msg = "设置失败: " + "; ".join(invalid_users)
            return False, error_msg
        
        # 重置所有非创建者的角色
        cursor.execute('''
            UPDATE organization_members
            SET role = ''
            WHERE org_id = ? AND role != 'creator'
        ''', (org_id,))
        
        # 设置新的管理员
        for admin_id in valid_admin_ids:
            cursor.execute('''
                UPDATE organization_members
                SET role = 'admin'
                WHERE org_id = ? AND user_id = ? AND role != 'creator'
            ''', (org_id, admin_id))
        
        conn.commit()
        
        if valid_admin_ids:
            return True, f"成功设置 {len(valid_admin_ids)} 名管理员"
        else:
            return True, "已重置所有管理员角色"
        
    except Exception as e:
        conn.rollback()
        return False, f"设置失败: {str(e)}"
    finally:
        conn.close()

def search_organization(org_id):
    """搜索组织"""
    return get_organization_details(org_id)

def create_join_request(org_id, user_id, message=""):
    """创建加入申请"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        user_id = normalize_user_id(user_id)
        
        # 检查是否已经是成员
        cursor.execute('''
            SELECT 1 FROM organization_members
            WHERE org_id = ? AND user_id = ?
        ''', (org_id, user_id))
        
        if cursor.fetchone():
            return False, "您已经是组织成员"
        
        # 检查是否已有待处理的申请
        cursor.execute('''
            SELECT 1 FROM join_requests
            WHERE org_id = ? AND user_id = ? AND status = 'pending'
        ''', (org_id, user_id))
        
        if cursor.fetchone():
            return False, "您已提交过申请，请等待审核"
        
        request_id = f"req_{str(uuid.uuid4())[:8]}"
        
        cursor.execute('''
            INSERT INTO join_requests (id, org_id, user_id, message)
            VALUES (?, ?, ?, ?)
        ''', (request_id, org_id, user_id, message))
        
        conn.commit()
        return True, "申请已提交，等待管理员审核"
        
    except Exception as e:
        conn.rollback()
        return False, f"提交失败: {str(e)}"
    finally:
        conn.close()

def create_invitation(org_id, inviter_id, invitee_id):
    """创建邀请"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        inviter_id = normalize_user_id(inviter_id)
        invitee_id = normalize_user_id(invitee_id)
        
        # 检查邀请者权限
        cursor.execute('''
            SELECT role FROM organization_members
            WHERE org_id = ? AND user_id = ?
        ''', (org_id, inviter_id))
        
        member = cursor.fetchone()
        if not member or member['role'] not in ['creator', 'admin']:
            return False, "权限不足"
        
        # 检查被邀请者是否已经是成员
        cursor.execute('''
            SELECT 1 FROM organization_members
            WHERE org_id = ? AND user_id = ?
        ''', (org_id, invitee_id))
        
        if cursor.fetchone():
            return False, "该用户已经是组织成员"
        
        # 检查是否已有待处理的邀请
        cursor.execute('''
            SELECT 1 FROM invitations
            WHERE org_id = ? AND invitee_id = ? AND status = 'pending'
        ''', (org_id, invitee_id))
        
        if cursor.fetchone():
            return False, "该用户已收到邀请"
        
        invitation_id = f"inv_{str(uuid.uuid4())[:8]}"
        
        cursor.execute('''
            INSERT INTO invitations (id, org_id, inviter_id, invitee_id)
            VALUES (?, ?, ?, ?)
        ''', (invitation_id, org_id, inviter_id, invitee_id))
        
        conn.commit()
        return True, "邀请已发送"
        
    except Exception as e:
        conn.rollback()
        return False, f"发送失败: {str(e)}"
    finally:
        conn.close()

def get_user_invitations(user_id):
    """获取用户收到的邀请"""
    conn = get_db_connection()
    user_conn = get_user_db_connection()
    cursor = conn.cursor()
    user_cursor = user_conn.cursor()
    
    try:
        user_id = normalize_user_id(user_id)
        
        cursor.execute('''
            SELECT i.id, i.org_id, o.name as org_name, 
                   i.inviter_id, i.created_at, i.message
            FROM invitations i
            JOIN organizations o ON i.org_id = o.id
            WHERE i.invitee_id = ? AND i.status = 'pending'
            ORDER BY i.created_at DESC
        ''', (user_id,))
        
        invitations = []
        for inv in cursor.fetchall():
            # 获取邀请者名称
            try:
                user_cursor.execute('''
                    SELECT nickname FROM users WHERE CAST(id AS TEXT) = ?
                ''', (normalize_user_id(inv['inviter_id']),))
                inviter_info = user_cursor.fetchone()
                inviter_name = inviter_info['nickname'] if inviter_info else '未知用户'
            except:
                inviter_name = '未知用户'
            
            invitations.append({
                'id': inv['id'],
                'orgId': inv['org_id'],
                'orgName': inv['org_name'],
                'inviter': inviter_name,
                'inviteTime': inv['created_at'],
                'message': inv['message'] or ''
            })
        
        return invitations, "success"
        
    except Exception as e:
        return [], f"获取失败: {str(e)}"
    finally:
        conn.close()
        user_conn.close()

def handle_invitation(invitation_id, user_id, action):
    """处理邀请"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        user_id = normalize_user_id(user_id)
        
        # 获取邀请信息
        cursor.execute('''
            SELECT org_id, invitee_id, status
            FROM invitations
            WHERE id = ?
        ''', (invitation_id,))
        
        invitation = cursor.fetchone()
        if not invitation:
            return False, "邀请不存在"
        
        if normalize_user_id(invitation['invitee_id']) != user_id:
            return False, "权限不足"
        
        if invitation['status'] != 'pending':
            return False, "邀请已处理"
        
        if action == 'accept':
            # 接受邀请，加入组织
            cursor.execute('''
                INSERT OR IGNORE INTO organization_members (org_id, user_id, role)
                VALUES (?, ?, '')
            ''', (invitation['org_id'], user_id))
            
            cursor.execute('''
                UPDATE invitations
                SET status = 'accepted'
                WHERE id = ?
            ''', (invitation_id,))
            
            message = "已加入组织"
            
        elif action == 'reject':
            # 拒绝邀请
            cursor.execute('''
                UPDATE invitations
                SET status = 'rejected'
                WHERE id = ?
            ''', (invitation_id,))
            
            message = "已拒绝邀请"
        else:
            return False, "无效的操作"
        
        conn.commit()
        return True, message
        
    except Exception as e:
        conn.rollback()
        return False, f"处理失败: {str(e)}"
    finally:
        conn.close()

def search_users(query):
    """搜索用户"""
    try:
        user_conn = get_user_db_connection()
        user_cursor = user_conn.cursor()
        
        # 检查用户表是否存在
        user_cursor.execute('''
            SELECT name FROM sqlite_master WHERE type='table' AND name='users'
        ''')
        
        if not user_cursor.fetchone():
            user_conn.close()
            return [], "用户表不存在"
        
        # 搜索用户
        user_cursor.execute('''
            SELECT id, nickname
            FROM users
            WHERE (CAST(id AS TEXT) LIKE ? OR nickname LIKE ?) AND id IS NOT NULL AND nickname IS NOT NULL
            LIMIT 20
        ''', (f'%{query}%', f'%{query}%'))
        
        users = []
        for user in user_cursor.fetchall():
            users.append({
                'id': str(user['id']),  # 统一转换为字符串
                'name': user['nickname'] or '未知用户',
                'avatarUrl': None
            })
        
        user_conn.close()
        return users, "success"
        
    except FileNotFoundError as e:
        return [], f"数据库文件不存在: {str(e)}"
    except Exception as e:
        return [], f"搜索失败: {str(e)}"

# 初始化数据库
if __name__ == "__main__":
    init_organization_db()

def get_organization_join_requests(org_id, user_id):
    """获取组织的加入申请列表"""
    conn = get_db_connection()
    user_conn = get_user_db_connection()
    cursor = conn.cursor()
    user_cursor = user_conn.cursor()
    
    try:
        user_id = normalize_user_id(user_id)
        
        # 检查用户是否有权限查看申请（创建者或管理员）
        cursor.execute('''
            SELECT role FROM organization_members
            WHERE org_id = ? AND user_id = ?
        ''', (org_id, user_id))
        
        member = cursor.fetchone()
        if not member or member['role'] not in ['creator', 'admin']:
            return [], "权限不足"
        
        # 获取待处理的申请
        cursor.execute('''
            SELECT jr.id, jr.user_id, jr.message, jr.created_at
            FROM join_requests jr
            WHERE jr.org_id = ? AND jr.status = 'pending'
            ORDER BY jr.created_at DESC
        ''', (org_id,))
        
        requests = []
        for req in cursor.fetchall():
            # 获取申请者信息
            try:
                user_cursor.execute('''
                    SELECT nickname FROM users WHERE CAST(id AS TEXT) = ?
                ''', (normalize_user_id(req['user_id']),))
                user_info = user_cursor.fetchone()
                user_name = user_info['nickname'] if user_info else '未知用户'
            except:
                user_name = '未知用户'
            
            requests.append({
                'id': req['id'],
                'userId': req['user_id'],
                'userName': user_name,
                'message': req['message'] or '',
                'requestTime': req['created_at']
            })
        
        return requests, "success"
        
    except Exception as e:
        return [], f"获取失败: {str(e)}"
    finally:
        conn.close()
        user_conn.close()

def handle_join_request(request_id, user_id, action):
    """处理加入申请"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        user_id = normalize_user_id(user_id)
        
        # 获取申请信息
        cursor.execute('''
            SELECT jr.org_id, jr.user_id, jr.status
            FROM join_requests jr
            WHERE jr.id = ?
        ''', (request_id,))
        
        request = cursor.fetchone()
        if not request:
            return False, "申请不存在"
        
        if request['status'] != 'pending':
            return False, "申请已处理"
        
        # 检查处理者权限
        cursor.execute('''
            SELECT role FROM organization_members
            WHERE org_id = ? AND user_id = ?
        ''', (request['org_id'], user_id))
        
        member = cursor.fetchone()
        if not member or member['role'] not in ['creator', 'admin']:
            return False, "权限不足"
        
        if action == 'accept':
            # 接受申请，将用户加入组织
            applicant_id = normalize_user_id(request['user_id'])
            
            cursor.execute('''
                INSERT OR IGNORE INTO organization_members (org_id, user_id, role)
                VALUES (?, ?, '')
            ''', (request['org_id'], applicant_id))
            
            cursor.execute('''
                UPDATE join_requests
                SET status = 'accepted'
                WHERE id = ?
            ''', (request_id,))
            
            message = "申请已通过，用户已加入组织"
            
        elif action == 'reject':
            # 拒绝申请
            cursor.execute('''
                UPDATE join_requests
                SET status = 'rejected'
                WHERE id = ?
            ''', (request_id,))
            
            message = "申请已拒绝"
        else:
            return False, "无效的操作"
        
        conn.commit()
        return True, message
        
    except Exception as e:
        conn.rollback()
        return False, f"处理失败: {str(e)}"
    finally:
        conn.close()

def get_user_organizations(user_id):
    """获取用户加入的组织列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        user_id = normalize_user_id(user_id)
        
        # 查询用户加入的所有组织
        cursor.execute('''
            SELECT o.id, o.name, COUNT(om.user_id) as member_count
            FROM organizations o
            JOIN organization_members om ON o.id = om.org_id
            WHERE o.id IN (
                SELECT org_id FROM organization_members WHERE user_id = ?
            )
            GROUP BY o.id, o.name
            ORDER BY o.name
        ''', (user_id,))
        
        organizations = []
        for org in cursor.fetchall():
            organizations.append({
                'id': org['id'],
                'name': org['name'],
                'members': org['member_count']
            })
        
        return organizations, "success"
        
    except Exception as e:
        print(f"获取用户组织列表失败: {str(e)}")
        return [], f"获取失败: {str(e)}"
    finally:
        conn.close()