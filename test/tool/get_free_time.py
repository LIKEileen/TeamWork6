import re
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict

import pandas as pd

from test.tool.constant import DAY_MAP, TIME_MAP
from test.tool.utils import merge_intervals, subtract_intervals


def get_remaining_work_time(
        workdays: Optional[List[str]] = None,
        start_hour: int = 9,
        end_hour: int = 18
) -> Dict[str, List[Tuple[int, int]]]:
    """
    获取从当前时间起，一周内每天剩余的工作时间（单位为分钟）。

    参数：
        workdays (Optional[List[str]]): 指定的工作日列表（如 ['Monday', 'Tuesday']），默认为周一至周五
        start_hour (int): 每天工作时间的起始小时（24小时制），默认 9 点
        end_hour (int): 每天工作时间的结束小时（24小时制），默认 18 点

    返回：
        Dict[str, List[Tuple[int, int]]]: 每个工作日对应的剩余工作时间区间，单位为分钟，格式为 [(开始分钟, 结束分钟)]
    """
    if workdays is None:
        workdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    now = datetime.now()
    weekday_idx = now.weekday()  # 0=Monday, 6=Sunday
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    result = {}
    for offset in range(7 - weekday_idx):
        day = now + timedelta(days=offset)
        day_name = day_names[day.weekday()]

        if day_name not in workdays:
            continue

        if offset == 0:
            current_minutes = day.hour * 60 + day.minute
            start_minutes = start_hour * 60
            end_minutes = end_hour * 60
            if current_minutes < end_minutes:
                interval_start = max(current_minutes, start_minutes)
                if interval_start < end_minutes:
                    result[day_name] = [(interval_start, end_minutes)]
        else:
            result[day_name] = [(start_hour * 60, end_hour * 60)]
    return result


def extract_schedule_from_excel(timetable: pd.DataFrame) -> Dict[str, List[Tuple[int, int]]]:
    """
    从 Excel 表格中提取每天的课程时间区间。

    参数：
        df (pd.DataFrame): Excel 表格读取后的 DataFrame，第一行为星期几，其余行为课程安排

    返回：
        Dict[str, List[Tuple[int, int]]]: 以星期为键，每天的上课时间区间列表为值，区间以分钟表示，如 [(540, 595), (610, 660)]
    """
    # 找出列号
    day_columns = {
        DAY_MAP.get(timetable.iloc[0, col], ""): col
        for col in range(1, timetable.shape[1])
        if timetable.iloc[0, col] in DAY_MAP
    }

    # 初始化所有星期为 key 的空列表
    result = {day: [] for day in DAY_MAP.values()}

    # 填充实际数据
    for day, col_idx in day_columns.items():
        for row_idx in range(1, timetable.shape[0]):
            cell = timetable.iat[row_idx, col_idx]
            if isinstance(cell, str):
                matches = re.findall(r'(\d+)-(\d+)节', cell)
                for match in matches:
                    start, end = map(int, match)
                    result[day].append((TIME_MAP[start][0], TIME_MAP[end][1]))
                result[day] = merge_intervals(result[day])
    return result


def get_free_time(
        remain_time: Dict[str, List[Tuple[int, int]]],
        schedule_time: Dict[str, List[Tuple[int, int]]],
        personal_time: Dict[str, List[Tuple[int, int]]]
) -> Dict[str, List[Tuple[int, int]]]:
    """
    根据剩余工作时间、课程时间和个人事务时间，计算每一天的空闲时间段。

    参数：
        remain_time (Dict[str, List[Tuple[int, int]]]): 每天的剩余工作时间，如 {"Monday": [(540, 1080)]}
        schedule_time (Dict[str, List[Tuple[int, int]]]): 每天的课程安排时间段
        personal_time (Dict[str, List[Tuple[int, int]]]): 每天的个人事务时间段

    返回：
        Dict[str, List[Tuple[int, int]]]: 每天的空闲时间段，已排除课程和个人时间后的可用时间
    """
    not_free_time = {}
    free_time = {}
    for key, value in schedule_time.items():
        not_free_time[key] = merge_intervals(value + personal_time[key])
    for key, value in remain_time.items():
        free_time[key] = subtract_intervals(value, not_free_time[key])
    return free_time
