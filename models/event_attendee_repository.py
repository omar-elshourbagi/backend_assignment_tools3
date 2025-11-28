import mysql.connector
from typing import List, Dict, Any
from datetime import time as time_type, timedelta
from database import get_db_connection, close_db
from config import DB_CONFIG

def convert_timedelta_to_time(td):
    """Convert timedelta to time object"""
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return time_type(hours, minutes, seconds)
    return td

class MysqlEventAttendeeRepository:
    def add_attendee(self, event_id: int, user_id: int, role: str, conn=None) -> int:
        local_conn = conn or get_db_connection()
        if not local_conn:
            raise Exception("Database connection failed")
        cursor = local_conn.cursor()
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "INSERT INTO event_attendees (event_id, user_id, role) VALUES (%s, %s, %s)",
                (event_id, user_id, role)
            )
            if conn is None:
                local_conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            if conn is None:
                close_db(local_conn)

    def get_attendees(self, event_id: int) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "SELECT user_id, role, attendance_status FROM event_attendees WHERE event_id = %s ORDER BY created_at ASC",
                (event_id,)
            )
            rows = cursor.fetchall() or []
            return [{"user_id": row["user_id"], "role": row["role"], "attendance_status": row.get("attendance_status", "pending")} for row in rows]
        finally:
            cursor.close()
            close_db(conn)

    def is_user_organizer(self, event_id: int, user_id: int) -> bool:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "SELECT 1 FROM event_attendees WHERE event_id = %s AND user_id = %s AND role = 'organizer' LIMIT 1",
                (event_id, user_id)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            close_db(conn)

    def is_user_attendee(self, event_id: int, user_id: int) -> bool:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "SELECT 1 FROM event_attendees WHERE event_id = %s AND user_id = %s LIMIT 1",
                (event_id, user_id)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            close_db(conn)

    def get_invited_events_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                """
                SELECT e.*
                FROM events e
                INNER JOIN event_attendees ea ON ea.event_id = e.id
                WHERE ea.user_id = %s AND ea.role = 'attendee'
                ORDER BY e.created_at DESC
                """,
                (user_id,)
            )
            events = list(cursor.fetchall() or [])
            # Convert timedelta to time for each event
            for event in events:
                if 'time' in event:
                    event['time'] = convert_timedelta_to_time(event['time'])
            return events
        finally:
            cursor.close()
            close_db(conn)

    def update_attendance_status(self, event_id: int, user_id: int, status: str) -> bool:
        """Update attendance status for an attendee"""
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "UPDATE event_attendees SET attendance_status = %s WHERE event_id = %s AND user_id = %s",
                (status, event_id, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            close_db(conn)

    def get_my_invitations(self, organizer_id: int) -> List[Dict[str, Any]]:
        """Get all people the organizer has invited across all their events with their status"""
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                """
                SELECT 
                    e.id as event_id,
                    e.title as event_title,
                    e.date as event_date,
                    u.id as invited_user_id,
                    u.name as invited_user_name,
                    u.email as invited_user_email,
                    ea.attendance_status,
                    ea.created_at as invited_at
                FROM events e
                INNER JOIN event_attendees ea ON ea.event_id = e.id
                INNER JOIN users u ON u.id = ea.user_id
                WHERE e.organizer_user_id = %s AND ea.role = 'attendee'
                ORDER BY e.date DESC, ea.created_at DESC
                """,
                (organizer_id,)
            )
            invitations = cursor.fetchall() or []
            return list(invitations)
        finally:
            cursor.close()
            close_db(conn)


