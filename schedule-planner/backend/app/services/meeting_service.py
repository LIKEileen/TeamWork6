import random
from ..services.schedule_service import mock_schedules

def find_meeting_times(members, duration, preferences):
    """模拟大模型推荐会议时间"""
    # 解析偏好（简化处理，实际应调用 llm_api_adapter）
    avoid_evening = "evening" in preferences.lower()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    hours = [f"{h:02d}:00" for h in range(8, 20 if not avoid_evening else 17)]

    suggestions = []
    for day in days:
        for hour in hours:
            conflict = False
            for member in members:
                if member not in mock_schedules:
                    continue
                for event in mock_schedules[member]:
                    if event["day"] == day and event["start"] <= hour < event["end"]:
                        conflict = True
                        break
                if conflict:
                    break
            if not conflict:
                suggestions.append({
                    "day": day,
                    "start": hour,
                    "end": f"{int(hour.split(':')[0]) + duration // 60:02d}:{duration % 60:02d}",
                    "score": random.uniform(0.7, 0.95)  # 模拟置信度
                })
    return suggestions[:3]  # 返回前3个可行时间
