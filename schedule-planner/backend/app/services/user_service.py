# Author: 唐震
from ..models.user import (
    update_user_info, 
    change_user_password, 
    update_user_avatar, 
    get_user_by_id,
    get_user_by_email, 
    get_user_by_phone, 
    bind_phone
)

from ..services.auth_service import verify_token
from ..config import Config
import os
import uuid
from werkzeug.utils import secure_filename
import re
import logging

def get_user_profile(token):
    """获取用户档案信息"""
    try:
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或 token 无效"
        
        user_id = payload['user_id']
        
        # 获取用户信息
        user = get_user_by_id(user_id)
        if not user:
            return None, "用户不存在"
        
        # 格式化返回数据
        user_profile = {
            'id': user['id'],
            'nickname': user['nickname'],
            'phone': user.get('phone'),
            'email': user['email'],
            'avatar': user.get('avatar') or Config.DEFAULT_AVATAR_URL,
            'role': user.get('role', 'user'),
            'created_at': user.get('created_at'),
            'updated_at': user.get('updated_at')
        }
        
        return user_profile, "获取用户信息成功"
        
    except Exception as e:
        logging.error(f"Error getting user profile: {str(e)}")
        return None, f"获取用户信息失败: {str(e)}"

def update_user_profile(token, nickname=None, phone=None, email=None):
    """更新用户档案信息"""
    try:
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或 token 无效"
        
        user_id = payload['user_id']
        
        # 构建更新数据
        updates = {}
        if nickname:
            updates['nickname'] = nickname
        if phone:
            # 验证手机号格式
            if not re.match(r'^1[3-9]\d{9}$', phone):
                return None, "手机号格式不正确"
            updates['phone'] = phone
        if email:
            # 验证邮箱格式
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return None, "邮箱格式不正确"
            updates['email'] = email
        
        if not updates:
            return None, "没有可更新的信息"
        
        # 更新用户信息
        updated_user, message = update_user_info(user_id, updates)
        if not updated_user:
            return None, message
        
        # 格式化返回数据
        user_profile = {
            'nickname': updated_user['nickname'],
            'phone': updated_user.get('phone'),
            'email': updated_user['email'],
            'avatar': updated_user.get('avatar') or Config.DEFAULT_AVATAR_URL,
        }
        
        return user_profile, "用户信息更新成功"
        
    except Exception as e:
        logging.error(f"Error updating user profile: {str(e)}")
        return None, f"更新用户信息失败: {str(e)}"

def change_password_service(token, old_password, new_password):
    """修改密码服务"""
    try:
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或 token 无效"
        
        user_id = payload['user_id']
        
        # 验证新密码格式
        if len(new_password) < 6:
            return None, "新密码长度至少为6位"
        
        # 调用模型层修改密码
        result, message = change_user_password(user_id, old_password, new_password)
        return result, message
        
    except Exception as e:
        logging.error(f"Error changing password: {str(e)}")
        return None, f"修改密码失败: {str(e)}"

def bind_phone_service(token, phone, verification_code):
    """绑定手机号服务"""
    try:
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或 token 无效"
        
        user_id = payload['user_id']
        
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return None, "手机号格式不正确"
        
        # 这里应该验证验证码，暂时跳过
        # TODO: 实现手机验证码验证逻辑
        
        # 绑定手机号
        updated_user, message = bind_phone(user_id, phone)
        if not updated_user:
            return None, message
        
        return True, message
        
    except Exception as e:
        logging.error(f"Error binding phone: {str(e)}")
        return None, f"绑定手机号失败: {str(e)}"

def upload_avatar(token, file):
    """上传用户头像"""
    try:
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或 token 无效"
        
        user_id = payload['user_id']
        
        # 验证文件
        if not file or not file.filename:
            return None, "请选择要上传的文件"
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return None, "只支持 PNG、JPG、JPEG、GIF、WEBP 格式的图片"
        
        # 检查文件大小 (最大 5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return None, "文件大小不能超过5MB"
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # 确保上传目录存在
        upload_folder = os.path.join('uploads', 'avatars')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 生成访问URL
        avatar_url = f"/uploads/avatars/{unique_filename}"
        
        # 更新用户头像
        updated_user, message = update_user_avatar(user_id, avatar_url)
        if not updated_user:
            # 如果数据库更新失败，删除已上传的文件
            try:
                os.remove(file_path)
            except:
                pass
            return None, message
        
        return avatar_url, "头像上传成功"
        
    except Exception as e:
        logging.error(f"Error uploading avatar: {str(e)}")
        return None, f"头像上传失败: {str(e)}"

def update_qq_avatar_service(token, avatar_url):
    """使用QQ头像服务"""
    try:
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或 token 无效"
        
        user_id = payload['user_id']
        
        # 验证QQ头像URL格式
        import re
        qq_avatar_pattern = r'^https?://(q\.qlogo\.cn|qlogo\.cn)'
        if not re.match(qq_avatar_pattern, avatar_url):
            # 允许其他有效的头像URL格式
            if not avatar_url.startswith(('http://', 'https://')):
                return None, "头像链接格式不正确"
        
        # 验证URL是否可访问
        try:
            import requests
            response = requests.head(avatar_url, timeout=10)
            if response.status_code not in [200, 302]:
                return None, "头像链接无法访问"
            
            # 检查是否为图片类型
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return None, "链接不是有效的图片"
                
        except requests.RequestException:
            # 如果无法验证，仍然允许保存（可能是防盗链等原因）
            logging.warning(f"Cannot verify avatar URL: {avatar_url}")
        
        # 更新用户头像
        updated_user, message = update_user_avatar(user_id, avatar_url)
        if not updated_user:
            return None, message
        
        return True, "QQ头像已更新"
        
    except Exception as e:
        logging.error(f"Error updating QQ avatar: {str(e)}")
        return None, f"更新QQ头像失败: {str(e)}"

def validate_phone_format(phone):
    """验证手机号格式"""
    if not phone:
        return False
    
    # 中国大陆手机号格式验证
    phone_pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(phone_pattern, phone))

def validate_email_format(email):
    """验证邮箱格式"""
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def get_user_statistics(user_id):
    """获取用户统计信息"""
    try:
        # 这里可以添加用户相关的统计信息
        # 比如：创建的日程数量、完成的任务数量等
        # 目前返回基础信息
        
        user = get_user_by_id(user_id)
        if not user:
            return None, "用户不存在"
        
        stats = {
            'user_id': user_id,
            'join_date': user.get('created_at'),
            'last_update': user.get('updated_at'),
            'profile_completion': calculate_profile_completion(user)
        }
        
        return stats, "获取统计信息成功"
        
    except Exception as e:
        logging.error(f"Error getting user statistics: {str(e)}")
        return None, f"获取统计信息失败: {str(e)}"

def calculate_profile_completion(user):
    """计算用户资料完整度"""
    try:
        total_fields = 5  # 昵称、邮箱、手机号、头像、角色
        completed_fields = 0
        
        if user.get('nickname'):
            completed_fields += 1
        if user.get('email'):
            completed_fields += 1
        if user.get('phone'):
            completed_fields += 1
        if user.get('avatar') and user.get('avatar') != Config.DEFAULT_AVATAR_URL:
            completed_fields += 1
        if user.get('role'):
            completed_fields += 1
        
        completion_rate = (completed_fields / total_fields) * 100
        return round(completion_rate, 1)
        
    except Exception as e:
        logging.error(f"Error calculating profile completion: {str(e)}")
        return 0.0