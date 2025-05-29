from typing import List, Tuple


def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    合并一组可能重叠的时间区间。

    参数：
        intervals (list of tuple): 时间区间列表，每个区间表示为 (开始时间, 结束时间)

    返回：
        list of tuple: 合并后的不重叠时间区间列表，按起始时间升序排列
    """
    if not intervals:
        return []

    # 先按起点排序
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for current in intervals[1:]:
        prev_start, prev_end = merged[-1]
        curr_start, curr_end = current

        if curr_start <= prev_end:  # 有重叠或相邻
            merged[-1] = (prev_start, max(prev_end, curr_end))  # 合并
        else:
            merged.append(current)

    return merged


def subtract_intervals(
        source: List[Tuple[int, int]],
        to_subtract: List[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """
    从源时间区间中扣除指定的时间区间，返回剩余的、不重叠的时间段。

    参数：
        source (List[tuple]): 原始时间区间列表，每个区间为 (开始时间, 结束时间)
        to_subtract (List[tuple]): 要扣除的时间区间列表，每个区间为 (开始时间, 结束时间)

    返回：
        List[tuple]: 从 source 中去除 to_subtract 后剩余的时间区间列表
    """
    result = []

    for start, end in source:
        current = [(start, end)]
        for s_start, s_end in to_subtract:
            temp = []
            for c_start, c_end in current:
                # 如果没有交集，保留原区间
                if s_end <= c_start or s_start >= c_end:
                    temp.append((c_start, c_end))
                else:
                    # 有交集，切割掉重叠部分
                    if c_start < s_start:
                        temp.append((c_start, s_start))
                    if s_end < c_end:
                        temp.append((s_end, c_end))
            current = temp
        result.extend(current)

    return result


def intersect_intervals(
        source: List[Tuple[int, int]],
        target: List[Tuple[int, int]]
) -> List[tuple]:
    """
    计算两个时间区间列表的交集。

    参数：
        source (List[tuple]): 第一个时间区间列表，每个区间为 (开始时间, 结束时间)
        target (List[tuple]): 第二个时间区间列表，每个区间为 (开始时间, 结束时间)

    返回：
        List[tuple]: 两个列表中所有可能的交集区间组成的列表
    """
    result = []

    for a_start, a_end in source:
        for b_start, b_end in target:
            # 计算交集的起点和终点
            start = max(a_start, b_start)
            end = min(a_end, b_end)
            if start < end:  # 有交集
                result.append((start, end))

    return result
