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
    """添加单个日程事件"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证输入数据
    if not title or not date or not start or not end:
        return None, "缺少必填字段"
    
    # 验证标题长度
    if len(title) > 100:
        return None, "事件名称长度不能超过100个字符"
    
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
    """添加长期重复事件"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return None, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证输入数据
    if not title or not start or not end or not frequency:
        return None, "缺少必填字段"
    
    # 验证标题长度
    if len(title) > 100:
        return None, "事件名称长度不能超过100个字符"
    
    # 验证频率
    valid_frequencies = ['daily', 'weekly', 'monthly', 'custom']
    if frequency not in valid_frequencies:
        return None, "无效的重复频率"
    
    # 验证自定义日期
    if frequency == 'custom':
        if not custom_dates:
            return None, "自定义频率必须提供日期列表"
        if isinstance(custom_dates, list):
            # 验证日期格式
            for date in custom_dates:
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    return None, f"无效的日期格式: {date}"
    
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
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    # 验证事件ID
    if not event_id or not isinstance(event_id, (int, str)):
        return False, "无效的事件ID"
    
    try:
        event_id = int(event_id)
    except ValueError:
        return False, "事件ID必须是数字"
    
    # 删除事件
    success, message = delete_schedule_event(user_id, event_id)
    
    return success, message

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

def import_excel_schedule(token, file_path):
    """从Excel文件导入日程"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        return False, "用户未登录或 token 无效"
    
    user_id = payload['user_id']
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 验证必需的列
        required_columns = ['标题', '日期', '开始时间', '结束时间']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"Excel文件缺少必需的列: {', '.join(missing_columns)}"
        
        success_count = 0
        error_count = 0
        errors = []
        
        # 逐行处理数据
        for index, row in df.iterrows():
            try:
                title = str(row['标题']).strip()
                date = str(row['日期'])
                start_time = str(row['开始时间'])
                end_time = str(row['结束时间'])
                color = str(row.get('颜色', '#409EFF'))
                
                # 验证数据
                if not title or title == 'nan':
                    errors.append(f"第{index+2}行: 标题不能为空")
                    error_count += 1
                    continue
                
                # 处理日期格式
                if '/' in date:
                    date = date.replace('/', '-')
                
                # 验证并格式化时间
                try:
                    # 处理时间格式 (可能是 HH:MM 或 HH:MM:SS)
                    if ':' not in start_time:
                        start_time = f"{start_time}:00"
                    if ':' not in end_time:
                        end_time = f"{end_time}:00"
                    
                    # 截取到分钟
                    start_time = ':'.join(start_time.split(':')[:2])
                    end_time = ':'.join(end_time.split(':')[:2])
                    
                    datetime.strptime(date, '%Y-%m-%d')
                    datetime.strptime(start_time, '%H:%M')
                    datetime.strptime(end_time, '%H:%M')
                except ValueError:
                    errors.append(f"第{index+2}行: 日期或时间格式错误")
                    error_count += 1
                    continue
                
                # 创建事件
                event, message = create_schedule_event(user_id, title, date, start_time, end_time, color, force_create=True)
                if event:
                    success_count += 1
                else:
                    errors.append(f"第{index+2}行: {message}")
                    error_count += 1
                    
            except Exception as e:
                errors.append(f"第{index+2}行: 处理失败 - {str(e)}")
                error_count += 1
        
        # 删除临时文件
        try:
            os.remove(file_path)
        except:
            pass
        
        if success_count > 0:
            result_message = f"导入完成：成功{success_count}条"
            if error_count > 0:
                result_message += f"，失败{error_count}条"
            return True, result_message
        else:
            return False, f"导入失败：{errors[0] if errors else '未知错误'}"
            
    except Exception as e:
        # 删除临时文件
        try:
            os.remove(file_path)
        except:
            pass
        return False, f"处理Excel文件失败: {str(e)}"

# 初始化数据库
init_schedule_db()