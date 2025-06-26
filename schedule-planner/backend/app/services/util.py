from typing import List, Tuple

TIME_MAP = {
    1: (480, 525),  # 8:00-8:45
    2: (530, 575),  # 8:50-9:35
    3: (590, 635),  # 9:50-10:35
    4: (640, 685),  # 10:40-11:25
    5: (690, 735),  # 11:30-12:15
    6: (780, 825),  # 13:00-13:45
    7: (830, 875),  # 13:50-14:35
    8: (890, 935),  # 14:50-15:35
    9: (940, 985),  # 15:40-16:25
    10: (990, 1035),  # 16:30-17:15
    11: (1080, 1125),  # 18:00-18:45
    12: (1130, 1175),  # 18:50-19:35
    13: (1180, 1225),  # 20:00-20:45
    14: (1230, 1275),  # 20:50-21:35
}

DAY_MAP = {
    "星期一": "Monday", "星期二": "Tuesday", "星期三": "Wednesday",
    "星期四": "Thursday", "星期五": "Friday", "星期六": "Saturday", "星期天": "Sunday"
}

DAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    合并一组可能重叠的时间区间。
    """
    if not intervals:
        return []

    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for current in intervals[1:]:
        prev_start, prev_end = merged[-1]
        curr_start, curr_end = current

        if curr_start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, curr_end))
        else:
            merged.append(current)

    return merged


def subtract_intervals(
        source: List[Tuple[int, int]],
        to_subtract: List[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """
    从源时间区间中扣除指定的时间区间。
    """
    result = []

    for start, end in source:
        current = [(start, end)]
        for s_start, s_end in to_subtract:
            temp = []
            for c_start, c_end in current:
                if s_end <= c_start or s_start >= c_end:
                    temp.append((c_start, c_end))
                else:
                    if c_start < s_start:
                        temp.append((c_start, s_start))
                    if s_end < c_end:
                        temp.append((s_end, c_end))
            current = temp
        result.extend(current)

    return result 