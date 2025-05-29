import pandas as pd
from ..services.schedule_service import mock_schedules

def process_schedule_file(file):
    """处理上传的日程文件，解析 CSV/Excel"""
    # 假设文件格式为：member,day,start,end,event
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format")

        # 解析并更新日程
        for _, row in df.iterrows():
            member = row['member']
            event = {
                "day": row['day'],
                "start": row['start'],
                "end": row['end'],
                "event": row['event']
            }
            if member not in mock_schedules:
                mock_schedules[member] = []
            mock_schedules[member].append(event)
        return {"status": "success", "message": f"Processed {len(df)} events"}
    except Exception as e:
        raise ValueError(f"File processing error: {str(e)}")