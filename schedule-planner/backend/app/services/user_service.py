from ..models.user import update_user_info, change_user_password, update_user_avatar, get_user_info
from ..services.auth_service import verify_token
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import logging

# 配置文件上传
UPLOAD_FOLDER = 'uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_user_profile(token, nickname, phone=None, email=None):
    """更新用户资料"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证输入数据
    if not nickname or not nickname.strip():
        return None, "昵称不能为空"
    
    nickname = nickname.strip()
    
    # 验证昵称长度
    if len(nickname) > 50:
        return None, "昵称长度不能超过50个字符"
    
    # 验证邮箱格式
    if email and email.strip():
        email = email.strip()
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return None, "邮箱格式不正确"
    else:
        email = None
    
    # 验证手机号格式
    if phone and phone.strip():
        phone = phone.strip()
        import re
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            return None, "手机号格式不正确"
    else:
        phone = None
    
    # 更新用户信息
    user_info, message = update_user_info(user_id, nickname, phone, email)
    
    if user_info:
        # 格式化返回数据
        return {
            'nickname': user_info['nickname'],
            'phone': user_info.get('phone'),
            'email': user_info.get('email'),
            'avatar': user_info.get('avatar')
        }, message
    else:
        return None, message

def change_password(token, old_password, new_password):
    """修改密码"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证输入数据
    if not old_password or not new_password:
        return False, "原密码和新密码不能为空"
    
    # 验证新密码强度
    if len(new_password) < 6:
        return False, "新密码长度至少6位"
    
    if len(new_password) > 100:
        return False, "新密码长度不能超过100位"
    
    # 修改密码
    success, message = change_user_password(user_id, old_password, new_password)
    
    return success, message

def upload_avatar(token, file):
    """上传头像"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证文件
    if not file or file.filename == '':
        return None, "没有选择文件"
    
    if not allowed_file(file.filename):
        return None, "不支持的文件格式，请上传 PNG、JPG、JPEG、GIF 或 WEBP 格式的图片"
    
    try:
        # 确保上传目录存在
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # 生成唯一文件名
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # 保存原始文件
        file.save(file_path)
        
        # 检查文件大小
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            os.remove(file_path)
            return None, "文件大小不能超过5MB"
        
        # 使用PIL验证和处理图片
        try:
            with Image.open(file_path) as img:
                # 验证是否为有效图片
                img.verify()
                
                # 重新打开图片进行处理
                with Image.open(file_path) as img:
                    # 转换为RGB模式（处理RGBA等格式）
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 限制图片尺寸（最大800x800）
                    max_size = (800, 800)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # 保存处理后的图片
                    processed_filename = f"avatar_{user_id}_{uuid.uuid4()}.jpg"
                    processed_file_path = os.path.join(UPLOAD_FOLDER, processed_filename)
                    img.save(processed_file_path, 'JPEG', quality=85, optimize=True)
                    
                    # 删除原始文件
                    os.remove(file_path)
                    
                    # 生成访问URL
                    avatar_url = f"/uploads/avatars/{processed_filename}"
                    
                    # 更新数据库
                    user_info, message = update_user_avatar(user_id, avatar_url)
                    
                    if user_info:
                        return avatar_url, "头像上传成功"
                    else:
                        # 删除已上传的文件
                        if os.path.exists(processed_file_path):
                            os.remove(processed_file_path)
                        return None, message
                        
        except Exception as img_error:
            # 删除无效文件
            if os.path.exists(file_path):
                os.remove(file_path)
            return None, f"图片处理失败: {str(img_error)}"
            
    except Exception as e:
        logging.error(f"Upload avatar error: {str(e)}")
        return None, f"文件上传失败: {str(e)}"

def get_user_profile(token):
    """获取用户资料"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 获取用户信息
    user_info = get_user_info(user_id)
    
    if user_info:
        return {
            'nickname': user_info['nickname'],
            'phone': user_info.get('phone'),
            'email': user_info.get('email'),
            'avatar': user_info.get('avatar'),
            'role': user_info.get('role')
        }, "获取成功"
    else:
        return None, "用户不存在"