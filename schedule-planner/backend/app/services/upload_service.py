# Author: 唐震
import os
import uuid
import logging
import pandas as pd
from werkzeug.utils import secure_filename
from ..config import Config
from ..services.auth_service import verify_token
from datetime import datetime

# 移除这行导入
# from ..services.schedule_service import mock_schedules

# 在文件内部创建模拟数据存储
mock_schedules = {}

def process_schedule_file(file, token):
    """处理日程文件上传"""
    try:
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或token无效"
        
        user_id = payload['user_id']
        
        if not file or not file.filename:
            return None, "请选择要上传的文件"
        
        # 检查文件类型
        allowed_extensions = {'csv', 'txt', 'json', 'xlsx', 'xls'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return None, "只支持 CSV、TXT、JSON、Excel 格式的文件"
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # 确保上传目录存在
        upload_folder = getattr(Config, 'UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 处理文件内容
        schedules_imported = 0
        try:
            if file_extension in ['xlsx', 'xls']:
                # 处理Excel文件
                schedules_imported = process_excel_file(file_path, user_id)
            elif file_extension == 'csv':
                # 处理CSV文件
                schedules_imported = process_csv_file(file_path, user_id)
            elif file_extension == 'json':
                # 处理JSON文件
                schedules_imported = process_json_file(file_path, user_id)
            else:
                # 处理文本文件
                schedules_imported = process_text_file(file_path, user_id)
        except Exception as process_error:
            logging.error(f"Error processing file content: {str(process_error)}")
            # 即使处理失败，文件上传成功
            schedules_imported = 0
        
        logging.info(f"Schedule file uploaded successfully: {unique_filename}")
        return {
            'filename': unique_filename,
            'original_filename': filename,
            'schedules_imported': schedules_imported,
            'file_path': file_path,
            'user_id': user_id
        }, "日程文件上传成功"
        
    except Exception as e:
        logging.error(f"Error processing schedule file: {str(e)}")
        return None, f"文件处理失败: {str(e)}"

def process_excel_file(file_path, user_id):
    """处理Excel文件"""
    try:
        # 使用pandas读取Excel文件
        df = pd.read_excel(file_path)
        schedules_imported = 0
        
        # 假设Excel文件有以下列：member, day, start, end, event
        for index, row in df.iterrows():
            try:
                # 获取数据
                member = str(row.get('member', f'user_{user_id}'))
                day = str(row.get('day', ''))
                start = str(row.get('start', ''))
                end = str(row.get('end', ''))
                event_name = str(row.get('event', ''))
                
                # 验证数据
                if not all([day, start, end, event_name]):
                    logging.warning(f"Row {index} missing required data")
                    continue
                
                # 创建事件对象
                event = {
                    "day": day,
                    "start": start,
                    "end": end,
                    "event": event_name,
                    "user_id": user_id
                }
                
                # 存储到模拟数据中
                if member not in mock_schedules:
                    mock_schedules[member] = []
                mock_schedules[member].append(event)
                schedules_imported += 1
                
            except Exception as row_error:
                logging.warning(f"Error processing row {index}: {str(row_error)}")
                continue
        
        logging.info(f"Processed {schedules_imported} events from Excel file")
        return schedules_imported
    except Exception as e:
        logging.error(f"Error processing Excel file: {str(e)}")
        return 0

def process_csv_file(file_path, user_id):
    """处理CSV文件"""
    try:
        df = pd.read_csv(file_path)
        schedules_imported = 0
        
        for index, row in df.iterrows():
            try:
                # 获取数据
                member = str(row.get('member', f'user_{user_id}'))
                day = str(row.get('day', ''))
                start = str(row.get('start', ''))
                end = str(row.get('end', ''))
                event_name = str(row.get('event', ''))
                
                # 验证数据
                if not all([day, start, end, event_name]):
                    logging.warning(f"Row {index} missing required data")
                    continue
                
                # 创建事件对象
                event = {
                    "day": day,
                    "start": start,
                    "end": end,
                    "event": event_name,
                    "user_id": user_id
                }
                
                # 存储到模拟数据中
                if member not in mock_schedules:
                    mock_schedules[member] = []
                mock_schedules[member].append(event)
                schedules_imported += 1
                
            except Exception as row_error:
                logging.warning(f"Error processing row {index}: {str(row_error)}")
                continue
        
        logging.info(f"Processed {schedules_imported} events from CSV file")
        return schedules_imported
    except Exception as e:
        logging.error(f"Error processing CSV file: {str(e)}")
        return 0

def process_json_file(file_path, user_id):
    """处理JSON文件"""
    try:
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        schedules_imported = 0
        if isinstance(data, list):
            for item in data:
                try:
                    # 验证JSON项目结构
                    if not isinstance(item, dict):
                        continue
                    
                    member = str(item.get('member', f'user_{user_id}'))
                    day = str(item.get('day', ''))
                    start = str(item.get('start', ''))
                    end = str(item.get('end', ''))
                    event_name = str(item.get('event', ''))
                    
                    # 验证数据
                    if not all([day, start, end, event_name]):
                        continue
                    
                    # 创建事件对象
                    event = {
                        "day": day,
                        "start": start,
                        "end": end,
                        "event": event_name,
                        "user_id": user_id
                    }
                    
                    # 存储到模拟数据中
                    if member not in mock_schedules:
                        mock_schedules[member] = []
                    mock_schedules[member].append(event)
                    schedules_imported += 1
                    
                except Exception as item_error:
                    logging.warning(f"Error processing JSON item: {str(item_error)}")
                    continue
        
        logging.info(f"Processed {schedules_imported} events from JSON file")
        return schedules_imported
    except Exception as e:
        logging.error(f"Error processing JSON file: {str(e)}")
        return 0

def process_text_file(file_path, user_id):
    """处理文本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        schedules_imported = 0
        for line_num, line in enumerate(lines):
            if line.strip():  # 跳过空行
                try:
                    # 假设文本格式为：member,day,start,end,event
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        member = parts[0].strip()
                        day = parts[1].strip()
                        start = parts[2].strip()
                        end = parts[3].strip()
                        event_name = parts[4].strip()
                        
                        # 创建事件对象
                        event = {
                            "day": day,
                            "start": start,
                            "end": end,
                            "event": event_name,
                            "user_id": user_id
                        }
                        
                        # 存储到模拟数据中
                        if member not in mock_schedules:
                            mock_schedules[member] = []
                        mock_schedules[member].append(event)
                        schedules_imported += 1
                        
                except Exception as line_error:
                    logging.warning(f"Error processing line {line_num + 1}: {str(line_error)}")
                    continue
        
        logging.info(f"Processed {schedules_imported} events from text file")
        return schedules_imported
    except Exception as e:
        logging.error(f"Error processing text file: {str(e)}")
        return 0

def get_mock_schedules():
    """获取模拟日程数据"""
    return mock_schedules

def clear_mock_schedules():
    """清空模拟日程数据"""
    global mock_schedules
    mock_schedules = {}
    return True, "模拟数据已清空"

# ... 保留其他所有现有函数 ...

def upload_avatar(file, token):
    """上传用户头像"""
    try:
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或token无效"
        
        user_id = payload['user_id']
        
        if not file or not file.filename:
            return None, "请选择要上传的文件"
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return None, "只支持 PNG、JPG、JPEG、GIF 格式的图片"
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"avatar_{user_id}_{uuid.uuid4().hex}.{file_extension}"
        
        # 设置头像上传目录
        avatar_folder = os.path.join('uploads', 'avatars')
        if not os.path.exists(avatar_folder):
            os.makedirs(avatar_folder)
        
        # 保存文件
        file_path = os.path.join(avatar_folder, unique_filename)
        file.save(file_path)
        
        # 生成访问URL
        avatar_url = f"/uploads/avatars/{unique_filename}"
        
        logging.info(f"Avatar uploaded successfully for user {user_id}: {unique_filename}")
        return {
            'filename': unique_filename,
            'original_filename': filename,
            'avatar_url': avatar_url,
            'file_path': file_path,
            'user_id': user_id
        }, "头像上传成功"
        
    except Exception as e:
        logging.error(f"Error uploading avatar: {str(e)}")
        return None, f"头像上传失败: {str(e)}"

def upload_general_file(file, token, upload_type='general'):
    """通用文件上传"""
    try:
        # 验证token
        payload = verify_token(token)
        if not payload:
            return None, "用户未登录或token无效"
        
        user_id = payload['user_id']
        
        if not file or not file.filename:
            return None, "请选择要上传的文件"
        
        # 根据上传类型设置允许的文件格式
        if upload_type == 'avatar':
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        elif upload_type == 'schedule':
            allowed_extensions = {'csv', 'txt', 'json', 'xlsx', 'xls'}
        else:
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx', 'xls'}
        
        # 检查文件类型
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return None, f"不支持的文件格式，允许的格式：{', '.join(allowed_extensions)}"
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{upload_type}_{user_id}_{uuid.uuid4().hex}.{file_extension}"
        
        # 设置上传目录
        if upload_type == 'avatar':
            upload_folder = os.path.join('uploads', 'avatars')
            file_url = f"/uploads/avatars/{unique_filename}"
        elif upload_type == 'schedule':
            upload_folder = os.path.join('uploads', 'schedules')
            file_url = f"/uploads/schedules/{unique_filename}"
        else:
            upload_folder = 'uploads'
            file_url = f"/uploads/{unique_filename}"
        
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        logging.info(f"File uploaded successfully: {unique_filename}")
        return {
            'filename': unique_filename,
            'original_filename': filename,
            'file_url': file_url,
            'file_path': file_path,
            'upload_type': upload_type,
            'user_id': user_id
        }, "文件上传成功"
        
    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")
        return None, f"文件上传失败: {str(e)}"