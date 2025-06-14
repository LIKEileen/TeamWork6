# Author: 唐震
import sqlite3
import datetime
import json
from ..config import Config

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 支持字典式访问
    return conn

def init_schedule_db():
    """初始化日程相关数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建日程事件表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            day TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            color TEXT DEFAULT '#409EFF',
            event_type TEXT DEFAULT 'single',
            recurring_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (recurring_id) REFERENCES recurring_events (id)
        )
    ''')
    
    # 创建长期重复事件表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recurring_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            frequency TEXT NOT NULL,
            custom_dates TEXT,
            color TEXT DEFAULT '#409EFF',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 创建索引提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedule_user_id ON schedule_events(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedule_day ON schedule_events(day)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recurring_user_id ON recurring_events(user_id)')
    
    conn.commit()
    conn.close()

def get_user_schedules(user_id, start_date=None, end_date=None):
    """获取用户的日程事件列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if start_date and end_date:
            cursor.execute('''
                SELECT id, title, day, start_time as start, end_time as end, color
                FROM schedule_events 
                WHERE user_id = ? AND day BETWEEN ? AND ?
                ORDER BY day, start_time
            ''', (user_id, start_date, end_date))
        else:
            cursor.execute('''
                SELECT id, title, day, start_time as start, end_time as end, color
                FROM schedule_events 
                WHERE user_id = ?
                ORDER BY day, start_time
            ''', (user_id,))
        
        events = cursor.fetchall()
        return [dict(event) for event in events]
        
    except Exception as e:
        print(f"Error getting user schedules: {str(e)}")
        return []
    finally:
        conn.close()

def check_time_conflict(user_id, day, start_time, end_time, exclude_event_id=None):
    """检查时间冲突"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 构建查询条件，排除当前正在编辑的事件
        if exclude_event_id:
            cursor.execute('''
                SELECT id, title, start_time, end_time 
                FROM schedule_events 
                WHERE user_id = ? AND day = ? AND id != ?
            ''', (user_id, day, exclude_event_id))
        else:
            cursor.execute('''
                SELECT id, title, start_time, end_time 
                FROM schedule_events 
                WHERE user_id = ? AND day = ?
            ''', (user_id, day))
        
        existing_events = cursor.fetchall()
        
        # 将时间字符串转换为分钟数便于比较
        def time_to_minutes(time_str):
            """将 HH:MM 格式转换为分钟数"""
            try:
                hour, minute = map(int, time_str.split(':'))
                return hour * 60 + minute
            except:
                return 0
        
        new_start = time_to_minutes(start_time)
        new_end = time_to_minutes(end_time)
        
        # 检查是否与现有事件冲突
        conflicts = []
        for event in existing_events:
            event_start = time_to_minutes(event['start_time'])
            event_end = time_to_minutes(event['end_time'])
            
            # 检查时间段是否重叠
            # 两个时间段重叠的条件：新事件开始时间 < 现有事件结束时间 AND 新事件结束时间 > 现有事件开始时间
            if new_start < event_end and new_end > event_start:
                conflicts.append({
                    'id': event['id'],
                    'title': event['title'],
                    'start_time': event['start_time'],
                    'end_time': event['end_time']
                })
        
        return conflicts
        
    except Exception as e:
        print(f"Error checking time conflict: {str(e)}")
        return []
    finally:
        conn.close()

def create_schedule_event(user_id, title, day, start_time, end_time, color='#409EFF', force_create=False):
    """创建单个日程事件（添加冲突检测）"""
    
    # 检查时间冲突（除非强制创建）
    if not force_create:
        conflicts = check_time_conflict(user_id, day, start_time, end_time)
        if conflicts:
            conflict_info = []
            for conflict in conflicts:
                conflict_info.append(f"《{conflict['title']}》({conflict['start_time']}-{conflict['end_time']})")
            return None, f"时间冲突：与以下事件重叠 - {', '.join(conflict_info)}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO schedule_events (user_id, title, day, start_time, end_time, color)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, title, day, start_time, end_time, color))
        
        event_id = cursor.lastrowid
        conn.commit()
        
        # 返回新创建的事件
        cursor.execute('''
            SELECT id, title, day, start_time as start, end_time as end, color
            FROM schedule_events WHERE id = ?
        ''', (event_id,))
        
        event = cursor.fetchone()
        return dict(event) if event else None, "创建成功"
        
    except Exception as e:
        print(f"Error creating schedule event: {str(e)}")
        return None, f"创建失败: {str(e)}"
    finally:
        conn.close()

def delete_schedule_event(user_id, event_id):
    """删除日程事件"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 首先检查事件是否存在且属于该用户
        cursor.execute('''
            SELECT id FROM schedule_events 
            WHERE id = ? AND user_id = ?
        ''', (event_id, user_id))
        
        event = cursor.fetchone()
        if not event:
            return False, "事件不存在或无权限删除"
        
        # 删除事件
        cursor.execute('''
            DELETE FROM schedule_events 
            WHERE id = ? AND user_id = ?
        ''', (event_id, user_id))
        
        if cursor.rowcount > 0:
            conn.commit()
            return True, "删除成功"
        else:
            return False, "删除失败"
            
    except Exception as e:
        print(f"Error deleting schedule event: {str(e)}")
        return False, f"删除失败: {str(e)}"
    finally:
        conn.close()

def create_recurring_event(user_id, title, start_time, end_time, frequency, custom_dates=None, color='#409EFF', repeat_count=None, force_create=False):
    """创建长期重复事件（添加冲突检测）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 插入长期事件记录
        cursor.execute('''
            INSERT INTO recurring_events (user_id, title, start_time, end_time, frequency, custom_dates, color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, title, start_time, end_time, frequency, custom_dates, color))
        
        recurring_id = cursor.lastrowid
        
        # 根据频率生成具体的日程事件（包含冲突检测）
        events_created, conflicts = _generate_recurring_events_with_conflict_check(
            cursor, user_id, recurring_id, title, start_time, end_time, 
            frequency, custom_dates, color, repeat_count, force_create
        )
        
        conn.commit()
        
        if conflicts and not force_create:
            conflict_summary = f"创建了{events_created}个事件，{len(conflicts)}个因时间冲突被跳过"
            return True, conflict_summary
        else:
            return True, f"成功创建{events_created}个重复事件"
        
    except Exception as e:
        print(f"Error creating recurring event: {str(e)}")
        return False, f"创建失败: {str(e)}"
    finally:
        conn.close()

def _generate_recurring_events_with_conflict_check(cursor, user_id, recurring_id, title, start_time, end_time, frequency, custom_dates, color, repeat_count=None, force_create=False):
    """根据频率生成具体的日程事件（包含冲突检测）"""
    events_created = 0
    conflicts = []
    today = datetime.date.today()
    
    # 设置默认重复次数
    if repeat_count is None:
        if frequency == 'daily':
            repeat_count = 30
        elif frequency == 'weekly':
            repeat_count = 12
        elif frequency == 'monthly':
            repeat_count = 12
    
    def try_create_event(event_date):
        """尝试创建单个事件"""
        nonlocal events_created, conflicts
        
        if not force_create:
            # 检查冲突
            day_conflicts = check_time_conflict(user_id, event_date, start_time, end_time)
            if day_conflicts:
                conflicts.append({
                    'date': event_date,
                    'conflicts': day_conflicts
                })
                return False
        
        # 创建事件
        cursor.execute('''
            INSERT INTO schedule_events (user_id, title, day, start_time, end_time, color, event_type, recurring_id)
            VALUES (?, ?, ?, ?, ?, ?, 'recurring', ?)
        ''', (user_id, title, event_date, start_time, end_time, color, recurring_id))
        events_created += 1
        return True
    
    if frequency == 'daily':
        for i in range(repeat_count):
            event_date = (today + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            try_create_event(event_date)
            
    elif frequency == 'weekly':
        for i in range(repeat_count):
            event_date = (today + datetime.timedelta(weeks=i)).strftime('%Y-%m-%d')
            try_create_event(event_date)
            
    elif frequency == 'monthly':
        for i in range(repeat_count):
            try:
                target_month = today.month + i
                target_year = today.year
                
                while target_month > 12:
                    target_month -= 12
                    target_year += 1
                
                try:
                    event_date = today.replace(year=target_year, month=target_month).strftime('%Y-%m-%d')
                except ValueError:
                    import calendar
                    last_day = calendar.monthrange(target_year, target_month)[1]
                    event_date = today.replace(year=target_year, month=target_month, day=min(today.day, last_day)).strftime('%Y-%m-%d')
                
                try_create_event(event_date)
                
            except Exception as e:
                print(f"Error creating monthly event for month {i}: {str(e)}")
                continue
            
    elif frequency == 'custom' and custom_dates:
        import json
        dates_list = json.loads(custom_dates) if isinstance(custom_dates, str) else custom_dates
        for date_str in dates_list:
            try_create_event(date_str)
    
    return events_created, conflicts