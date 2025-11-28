import mysql.connector
from typing import List, Dict, Any
from datetime import time as time_type, timedelta
import logging
from database import get_db_connection, close_db
from config import DB_CONFIG
from handlers.exceptions import DatabaseException

logger = logging.getLogger(__name__)

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
        """Add attendee with proper error handling"""
        local_conn = conn or get_db_connection()
        cursor = None
        try:
            cursor = local_conn.cursor()
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "INSERT INTO event_attendees (event_id, user_id, role) VALUES (%s, %s, %s)",
                (event_id, user_id, role)
            )
            if conn is None:
                local_conn.commit()
            attendee_id = cursor.lastrowid
            logger.info(f"Attendee added successfully: {attendee_id}")
            return attendee_id
        except mysql.connector.Error as err:
            if local_conn and conn is None:
                local_conn.rollback()
            if err.errno == 1062:  # Duplicate entry
                raise DatabaseException("User is already an attendee of this event")
            logger.error(f"Database error adding attendee: {err}")
            raise DatabaseException(f"Failed to add attendee: {err.msg}")
        except Exception as e:
            if local_conn and conn is None:
                local_conn.rollback()
            logger.error(f"Unexpected error adding attendee: {str(e)}")
            raise DatabaseException("Failed to add attendee")
        finally:
            if cursor:
                cursor.close()
            if conn is None:
                close_db(local_conn)

    def get_attendees(self, event_id: int) -> List[Dict[str, Any]]:
        """Get attendees with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "SELECT user_id, role, attendance_status FROM event_attendees WHERE event_id = %s ORDER BY created_at ASC",
                (event_id,)
            )
            rows = cursor.fetchall() or []
            return [{"user_id": row["user_id"], "role": row["role"], "attendance_status": row.get("attendance_status", "pending")} for row in rows]
        except mysql.connector.Error as err:
            logger.error(f"Database error getting attendees: {err}")
            raise DatabaseException(f"Failed to retrieve attendees: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error getting attendees: {str(e)}")
            raise DatabaseException("Failed to retrieve attendees")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)

    def is_user_organizer(self, event_id: int, user_id: int) -> bool:
        """Check if user is organizer with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "SELECT 1 FROM event_attendees WHERE event_id = %s AND user_id = %s AND role = 'organizer' LIMIT 1",
                (event_id, user_id)
            )
            return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            logger.error(f"Database error checking organizer: {err}")
            raise DatabaseException(f"Failed to check organizer status: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error checking organizer: {str(e)}")
            raise DatabaseException("Failed to check organizer status")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)

    def is_user_attendee(self, event_id: int, user_id: int) -> bool:
        """Check if user is attendee with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "SELECT 1 FROM event_attendees WHERE event_id = %s AND user_id = %s LIMIT 1",
                (event_id, user_id)
            )
            return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            logger.error(f"Database error checking attendee: {err}")
            raise DatabaseException(f"Failed to check attendee status: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error checking attendee: {str(e)}")
            raise DatabaseException("Failed to check attendee status")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)

    def get_invited_events_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get invited events for user with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
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
        except mysql.connector.Error as err:
            logger.error(f"Database error getting invited events: {err}")
            raise DatabaseException(f"Failed to retrieve invited events: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error getting invited events: {str(e)}")
            raise DatabaseException("Failed to retrieve invited events")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)

    def update_attendance_status(self, event_id: int, user_id: int, status: str) -> bool:
        """Update attendance status for an attendee with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                "UPDATE event_attendees SET attendance_status = %s WHERE event_id = %s AND user_id = %s",
                (status, event_id, user_id)
            )
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Attendance status updated for user {user_id} in event {event_id}")
            return success
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            logger.error(f"Database error updating attendance status: {err}")
            raise DatabaseException(f"Failed to update attendance status: {err.msg}")
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error updating attendance status: {str(e)}")
            raise DatabaseException("Failed to update attendance status")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)

    def get_my_invitations(self, organizer_id: int) -> List[Dict[str, Any]]:
        """Get all people the organizer has invited across all their events with their status"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
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
        except mysql.connector.Error as err:
            logger.error(f"Database error getting invitations: {err}")
            raise DatabaseException(f"Failed to retrieve invitations: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error getting invitations: {str(e)}")
            raise DatabaseException("Failed to retrieve invitations")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)


