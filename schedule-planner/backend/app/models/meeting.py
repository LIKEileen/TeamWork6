import datetime
import logging
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from ..config import Config


def get_db_connection() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise


def init_meeting_db() -> None:
    """初始化会议相关的数据库表。

    如果 'meetings' 和 'meeting_participants' 表不存在，则创建它们。
    同时为相关列创建索引以提高查询性能。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 创建会议表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                creator_id INTEGER NOT NULL,
                min_participants INTEGER DEFAULT 1,
                FOREIGN KEY (creator_id) REFERENCES users (id)
            )
        """)

        # 创建会议参与者表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meeting_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                is_key_member BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (meeting_id) REFERENCES meetings (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(meeting_id, user_id)
            )
        """)

        # 创建索引
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_meeting_creator ON meetings(creator_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_participant_meeting ON meeting_participants(meeting_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_participant_user ON meeting_participants(user_id)"
        )

        conn.commit()
        logging.info("Meeting database tables initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing meeting database: {str(e)}")
        raise
    finally:
        conn.close()


def get_meetings_by_user_id(
    user_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
) -> List[Dict[str, Any]]:
    """根据用户ID获取其参加的所有会议。

    可以根据开始和结束日期进行过滤。

    Args:
        user_id (int): 用户ID。
        start_date (Optional[datetime.date]): 查询的开始日期。
        end_date (Optional[datetime.date]): 查询的结束日期。

    Returns:
        List[Dict[str, Any]]: 包含会议信息的字典列表。每个字典代表一个会议，
                              并包含参与者列表。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 查询用户参与的会议ID
        cursor.execute(
            """
            SELECT meeting_id FROM meeting_participants WHERE user_id = ?
        """,
            (user_id,),
        )
        meeting_ids: List[str] = [row["meeting_id"] for row in cursor.fetchall()]

        if not meeting_ids:
            return []

        # 构建基于日期过滤的查询
        query = """
            SELECT m.id, m.title, m.description, m.start_time, m.end_time, m.creator_id
            FROM meetings m
            WHERE m.id IN ({})
        """.format(",".join("?" for _ in meeting_ids))

        params = list(meeting_ids)

        if start_date:
            query += " AND date(m.start_time) >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND date(m.start_time) <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY m.start_time"

        cursor.execute(query, params)
        meetings: List[Dict] = [dict(row) for row in cursor.fetchall()]

        # 为每个会议获取参与者列表
        for meeting in meetings:
            cursor.execute(
                """
                SELECT u.id, u.nickname, u.email
                FROM users u
                JOIN meeting_participants mp ON u.id = mp.user_id
                WHERE mp.meeting_id = ?
            """,
                (meeting["id"],),
            )
            participants = [dict(row) for row in cursor.fetchall()]
            meeting["participants"] = participants

        return meetings

    except Exception as e:
        logging.error(f"Error getting meetings for user {user_id}: {str(e)}")
        return []
    finally:
        conn.close()


def create_meeting_in_db(
    meeting_data: Dict[str, Any],
    creator_id: int,
    participant_ids: List[int],
    key_participant_ids: List[int],
) -> Tuple[Optional[Dict[str, Any]], str]:
    """在数据库中创建新会议及其参与者。

    Args:
        meeting_data (Dict[str, Any]): 包含会议信息的字典，如 title, description,
                                     start_time, end_time, min_participants。
        creator_id (int): 会议创建者的用户ID。
        participant_ids (List[int]): 参与者ID列表。
        key_participant_ids (List[int]): 关键参与者ID列表。

    Returns:
        Tuple[Optional[Dict[str, Any]], str]: 一个元组，第一个元素是创建的会议信息
                                             （如果成功），第二个元素是操作结果的消息。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 插入会议
        cursor.execute(
            """
            INSERT INTO meetings (title, description, start_time, end_time, creator_id, min_participants)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                meeting_data["title"],
                meeting_data.get("description"),
                meeting_data["start_time"],
                meeting_data["end_time"],
                creator_id,
                meeting_data.get("min_participants", 1),
            ),
        )
        meeting_id = cursor.lastrowid

        # 添加参与者 (包括创建者)
        all_participant_ids = set(participant_ids)
        all_participant_ids.add(creator_id)

        key_ids = set(key_participant_ids)

        for user_id in all_participant_ids:
            is_key = user_id in key_ids
            cursor.execute(
                """
                INSERT INTO meeting_participants (meeting_id, user_id, is_key_member)
                VALUES (?, ?, ?)
            """,
                (meeting_id, user_id, is_key),
            )

        conn.commit()

        # 返回创建的会议信息
        cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
        meeting = dict(cursor.fetchone())

        # 获取参与者信息
        participants_query = """
            SELECT u.id, u.nickname, u.email
            FROM users u
            JOIN meeting_participants mp ON u.id = mp.user_id
            WHERE mp.meeting_id = ?
        """
        cursor.execute(participants_query, (meeting_id,))
        participants = [dict(row) for row in cursor.fetchall()]
        meeting["participants"] = participants

        return meeting, "会议创建成功"

    except Exception as e:
        conn.rollback()
        logging.error(f"Error creating meeting in DB: {str(e)}")
        return None, f"创建会议失败: {str(e)}"
    finally:
        conn.close()
