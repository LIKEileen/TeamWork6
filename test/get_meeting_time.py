import os
from typing import List, Dict

import pandas as pd

from test.tool.get_free_time import get_free_time, get_remaining_work_time, extract_schedule_from_excel


def recursive_find(
        free_time_slots: List[Dict],
        duration: int
) -> List[int]:
    """
    递归式地在多个重要性等级的空闲时间段中，寻找连续 duration 分钟的最优起始时间点。

    参数：
    - free_time_slots: List[Dict]，每个字典包含：
        - 'important': int，表示该时间段的优先级，数值越大表示越重要；
        - 'free_time': List[Tuple[int, int]]，表示一个人在一天中的多个空闲时间段，单位为分钟，范围是 [0, 1440)，例如 (540, 600) 表示从上午9点到10点。
    - duration: int，表示希望安排的连续时间长度，单位为分钟。

    返回：
    - List[int]，可能的最优起始时间点列表，单位为分钟，可能有多个时间点具有同样的最大可行性。
    """

    # 初始化一个布尔数组，表示所有可能的开始时间点是否可用（长度为 1440 - duration + 1）
    available_begin = [True] * (60 * 24 + 1 - duration)

    # 获取所有不同的重要性等级，并按从高到低排序
    importance_levels = sorted({p['important'] for p in free_time_slots}, reverse=True)

    # 初始化最终可行的起始时间点列表
    available_begin_id = []

    # 对每个重要性等级从高到低依次处理
    for importance_level in importance_levels:
        # 用于统计每个起始时间点在当前优先级下出现的次数
        available_begin_count = [0] * (60 * 24 + 1 - duration)

        # 遍历所有空闲时间段，统计在当前重要性等级下的可用开始时间
        for slot in free_time_slots:
            if slot['important'] == importance_level:
                for start, end in slot['free_time']:
                    # 在该空闲段中查找所有可安排 duration 长度的起始时间点
                    for i in range(max(0, start), min(60 * 24 - duration, end - duration + 1)):
                        if available_begin[i]:  # 如果在前一重要性等级中此时间点仍可用
                            available_begin_count[i] += 1

        # 找到当前优先级下最多人可用的时间点数值（即最匹配的时间点）
        max_count = max(available_begin_count)

        # 如果存在可用时间点，则更新列表
        if max_count > 0:
            available_begin_id = [i for i, count in enumerate(available_begin_count) if count == max_count]
        else:
            # 如果当前优先级下没有可行时间点，则返回之前记录的时间点
            return available_begin_id

        # 将下一轮的可用起始时间点限制在当前优先级下的最优解中
        available_begin = [i in available_begin_id for i in range(len(available_begin))]

    # 返回最终所有优先级筛选后的可用起始时间点
    return available_begin_id


def get_meeting_time(
        everyone_schedule: List[Dict],
        duration: int
) -> Dict[str, List[int]]:
    """
    计算一周内每一天所有成员都可参与会议的时间段，满足给定的会议时长要求。

    参数：
       everyone_schedule (list): 包含每个人日程信息的列表。每个元素是一个字典，包含：
           - 'id': 人员唯一标识
           - 'important': 是否为关键人员（可用于优先级判断）
           - 'schedule_time': 工作相关的日程安排
           - 'personal_time': 个人事务安排
       duration (int): 会议所需的持续时间（单位：分钟）

    返回：
       dict: 一个字典，键为星期几（如 'Monday'），值为当天所有人可参与会议开始时间，
    """
    remain_time = get_remaining_work_time()

    # 获取每个人每天的空闲时间
    person_free_time_list = []
    for person in everyone_schedule:
        person_free_time = {}
        person_free_time['id'] = person['id']
        person_free_time['important'] = person['important']
        person_free_time['free_time'] = get_free_time(
            remain_time,
            person["schedule_time"],
            person["personal_time"]
        )
        person_free_time_list.append(person_free_time)

    # 获取每天每个人的空闲时间
    everyday_free_time_list = {}
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        everyday_free_time = []
        for raw_person_free_time in person_free_time_list:
            person_free_time = {}
            person_free_time['id'] = raw_person_free_time['id']
            person_free_time['important'] = raw_person_free_time['important']
            person_free_time['free_time'] = raw_person_free_time['free_time'].get(day, [])
            everyday_free_time.append(person_free_time)
        everyday_free_time_list[day] = everyday_free_time

    # 获取每天的可开会时间
    available_meeting_time = {}
    for key, value in everyday_free_time_list.items():
        available_meeting_time[key] = recursive_find(value, duration)
    return available_meeting_time


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    timetable_path = os.path.join(base_dir, "demo_timetable", "CP5SQ0gV.xlsx")
    timetable = pd.read_excel(timetable_path)
    schedule = extract_schedule_from_excel(timetable)

    everyone_schedule = [
        {
            "id": 0,
            "important": 1,
            "schedule_time": schedule,
            "personal_time": {
                'Monday': [(480, 600)], 'Tuesday': [],
                'Wednesday': [(480, 600), (630, 720)], 'Thursday': [(480, 600)],
                'Friday': [], 'Saturday': [], 'Sunday': []
            }
        },
        {
            "id": 1,
            "important": 1,
            "schedule_time": schedule,
            "personal_time": {
                'Monday': [(480, 600)], 'Tuesday': [],
                'Wednesday': [(480, 600), (630, 720)], 'Thursday': [(480, 600)],
                'Friday': [], 'Saturday': [], 'Sunday': []
            }
        },
        {
            "id": 2,
            "important": 0,
            "schedule_time": schedule,
            "personal_time": {
                'Monday': [(480, 1020)], 'Tuesday': [(480, 1020)], 'Wednesday': [(480, 1020)],
                'Thursday': [(480, 1020)], 'Friday': [(480, 1020)], 'Saturday': [], 'Sunday': []
            }
        },
        {
            "id": 3,
            "important": 1,
            "schedule_time": schedule,
            "personal_time": {
                'Monday': [(480, 730)], 'Tuesday': [(700, 900)],
                'Wednesday': [(480, 600)], 'Thursday': [], 'Friday': [(480, 720)],
                'Saturday': [], 'Sunday': []
            }
        },
        {
            "id": 4,
            "important": 0,
            "schedule_time": schedule,
            "personal_time": {
                'Monday': [], 'Tuesday': [], 'Wednesday': [],
                'Thursday': [], 'Friday': [], 'Saturday': [(800, 1100)], 'Sunday': [(800, 1100)]
            }
        }
    ]
    available_meeting_start_time = get_meeting_time(everyone_schedule, 40)
    print(available_meeting_start_time)
