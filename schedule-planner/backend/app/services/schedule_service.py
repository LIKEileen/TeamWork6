from ..models.schedule import (
    get_user_schedules, create_schedule_event, delete_schedule_event, 
    create_recurring_event, init_schedule_db, check_time_conflict
)
from ..services.auth_service import verify_token
import pandas as pd
import json
import os
from datetime import datetime

def get_user_schedule_list(token, start_date=None, end_date=None):
    """获取用户日程列表"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 获取日程数据
    schedules = get_user_schedules(user_id, start_date, end_date)
    
    return schedules, "success"

def add_single_schedule_event(token, title, date, start, end, color='#409EFF', force_create=False):
    """添加单个日程事件（包含冲突检测）"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证输入数据
    if not title or not date or not start or not end:
        return None, "缺少必填字段"
    
    # 验证时间格式
    try:
        datetime.strptime(date, '%Y-%m-%d')
        datetime.strptime(start, '%H:%M')
        datetime.strptime(end, '%H:%M')
    except ValueError:
        return None, "日期或时间格式错误"
    
    # 验证时间逻辑
    start_minutes = sum(x * int(t) for x, t in zip([60, 1], start.split(':')))
    end_minutes = sum(x * int(t) for x, t in zip([60, 1], end.split(':')))
    
    if start_minutes >= end_minutes:
        return None, "结束时间必须晚于开始时间"
    
    # 创建事件（包含冲突检测）
    event, message = create_schedule_event(user_id, title, date, start, end, color, force_create)
    
    return event, message

def add_recurring_schedule_event(token, title, start, end, frequency, custom_dates=None, color='#409EFF', repeat_count=None, force_create=False):
    """添加长期重复事件（包含冲突检测）"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证输入数据
    if not title or not start or not end or not frequency:
        return None, "缺少必填字段"
    
    # 验证频率
    valid_frequencies = ['daily', 'weekly', 'monthly', 'custom']
    if frequency not in valid_frequencies:
        return None, "无效的重复频率"
    
    if frequency == 'custom' and not custom_dates:
        return None, "自定义频率需要提供日期列表"
    
    # 验证重复次数
    if repeat_count is not None:
        try:
            repeat_count = int(repeat_count)
            if repeat_count <= 0:
                return None, "重复次数必须大于0"
            if repeat_count > 365:
                return None, "重复次数不能超过365次"
        except (ValueError, TypeError):
            return None, "重复次数必须是有效的数字"
    
    # 验证时间格式
    try:
        datetime.strptime(start, '%H:%M')
        datetime.strptime(end, '%H:%M')
    except ValueError:
        return None, "时间格式错误"
    
    # 验证时间逻辑
    start_minutes = sum(x * int(t) for x, t in zip([60, 1], start.split(':')))
    end_minutes = sum(x * int(t) for x, t in zip([60, 1], end.split(':')))
    
    if start_minutes >= end_minutes:
        return None, "结束时间必须晚于开始时间"
    
    # 处理自定义日期
    if frequency == 'custom' and custom_dates:
        if isinstance(custom_dates, list):
            custom_dates = json.dumps(custom_dates)
    
    # 创建重复事件（包含冲突检测）
    success, message = create_recurring_event(user_id, title, start, end, frequency, custom_dates, color, repeat_count, force_create)
    
    return success, message

def remove_schedule_event(token, event_id):
    """删除日程事件"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 删除事件
    success, message = delete_schedule_event(user_id, event_id)
    
    return success, message

def import_excel_schedule(token, file_path):
    """从Excel文件导入日程"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 验证必要的列
        required_columns = ['title', 'date', 'start_time', 'end_time']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"Excel文件缺少必要列: {', '.join(missing_columns)}"
        
        imported_count = 0
        errors = []
        
        # 逐行处理数据
        for index, row in df.iterrows():
            try:
                title = str(row['title']).strip()
                date = str(row['date'])
                start_time = str(row['start_time'])
                end_time = str(row['end_time'])
                color = str(row.get('color', '#409EFF'))
                
                # 处理日期格式
                if isinstance(row['date'], pd.Timestamp):
                    date = row['date'].strftime('%Y-%m-%d')
                
                # 处理时间格式
                if isinstance(row['start_time'], pd.Timestamp):
                    start_time = row['start_time'].strftime('%H:%M')
                elif ':' not in start_time:
                    start_time = f"{start_time}:00"
                
                if isinstance(row['end_time'], pd.Timestamp):
                    end_time = row['end_time'].strftime('%H:%M')
                elif ':' not in end_time:
                    end_time = f"{end_time}:00"
                
                # 验证数据
                if not title or title == 'nan':
                    errors.append(f"第{index+2}行：标题不能为空")
                    continue
                
                # 创建事件
                event = create_schedule_event(user_id, title, date, start_time, end_time, color)
                if event:
                    imported_count += 1
                else:
                    errors.append(f"第{index+2}行：创建事件失败")
                    
            except Exception as e:
                errors.append(f"第{index+2}行：{str(e)}")
        
        # 删除临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if imported_count > 0:
            message = f"成功导入{imported_count}个事件"
            if errors:
                message += f"，{len(errors)}个错误"
            return True, message
        else:
            return None, "导入失败：" + "; ".join(errors[:5])  # 只显示前5个错误
            
    except Exception as e:
        # 删除临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
        return None, f"文件处理失败: {str(e)}"

def check_schedule_conflict(token, date, start, end, exclude_event_id=None):
    """检查日程冲突"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证时间格式
    try:
        datetime.strptime(date, '%Y-%m-%d')
        datetime.strptime(start, '%H:%M')
        datetime.strptime(end, '%H:%M')
    except ValueError:
        return None, "日期或时间格式错误"
    
    # 验证时间逻辑
    start_minutes = sum(x * int(t) for x, t in zip([60, 1], start.split(':')))
    end_minutes = sum(x * int(t) for x, t in zip([60, 1], end.split(':')))
    
    if start_minutes >= end_minutes:
        return None, "结束时间必须晚于开始时间"
    
    # 检查冲突
    conflicts = check_time_conflict(user_id, date, start, end, exclude_event_id)
    
    return conflicts, "检查完成"

# 初始化数据库
init_schedule_db()