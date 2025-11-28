import mysql.connector
from typing import Optional, Dict, Any, List
from datetime import date, time as time_type, timedelta
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

class MysqlEventRepository:
    def create_event(self, organizer_user_id: int, title: str, date_value: date, time_value: time_type, location: str, description: Optional[str], conn=None) -> Dict[str, Any]:
        """Create event with proper error handling"""
        local_conn = conn or get_db_connection()
        cursor = None
        try:
            cursor = local_conn.cursor()
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                '''
                INSERT INTO events (title, date, time, location, description, organizer_user_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ''',
                (title, date_value, time_value, location, description, organizer_user_id)
            )
            if conn is None:
                local_conn.commit()
            event_id = cursor.lastrowid
            logger.info(f"Event created successfully: {event_id}")
            return {
                "id": event_id,
                "title": title,
                "date": date_value,
                "time": time_value,
                "location": location,
                "description": description,
                "organizer_user_id": organizer_user_id
            }
        except mysql.connector.Error as err:
            if local_conn and conn is None:
                local_conn.rollback()
            logger.error(f"Database error creating event: {err}")
            raise DatabaseException(f"Failed to create event: {err.msg}")
        except Exception as e:
            if local_conn and conn is None:
                local_conn.rollback()
            logger.error(f"Unexpected error creating event: {str(e)}")
            raise DatabaseException("Failed to create event")
        finally:
            if cursor:
                cursor.close()
            if conn is None:
                close_db(local_conn)

    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get event by ID with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
            event = cursor.fetchone()
            if event and 'time' in event:
                event['time'] = convert_timedelta_to_time(event['time'])
            return event if event else None
        except mysql.connector.Error as err:
            logger.error(f"Database error getting event by ID: {err}")
            raise DatabaseException(f"Failed to retrieve event: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error getting event by ID: {str(e)}")
            raise DatabaseException("Failed to retrieve event")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)

    def get_events_by_organizer(self, user_id: int) -> List[Dict[str, Any]]:
        """Get events by organizer with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute("SELECT * FROM events WHERE organizer_user_id = %s ORDER BY created_at DESC", (user_id,))
            events = cursor.fetchall() or []
            # Convert timedelta to time for each event
            for event in events:
                if 'time' in event:
                    event['time'] = convert_timedelta_to_time(event['time'])
            return list(events)
        except mysql.connector.Error as err:
            logger.error(f"Database error getting events by organizer: {err}")
            raise DatabaseException(f"Failed to retrieve events: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error getting events by organizer: {str(e)}")
            raise DatabaseException("Failed to retrieve events")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)

    def delete_event(self, event_id: int, conn=None) -> None:
        """Delete event with proper error handling"""
        local_conn = conn or get_db_connection()
        cursor = None
        try:
            cursor = local_conn.cursor()
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
            if conn is None:
                local_conn.commit()
            if cursor.rowcount == 0:
                logger.warning(f"Attempted to delete non-existent event: {event_id}")
            else:
                logger.info(f"Event deleted successfully: {event_id}")
        except mysql.connector.Error as err:
            if local_conn and conn is None:
                local_conn.rollback()
            logger.error(f"Database error deleting event: {err}")
            raise DatabaseException(f"Failed to delete event: {err.msg}")
        except Exception as e:
            if local_conn and conn is None:
                local_conn.rollback()
            logger.error(f"Unexpected error deleting event: {str(e)}")
            raise DatabaseException("Failed to delete event")
        finally:
            if cursor:
                cursor.close()
            if conn is None:
                close_db(local_conn)

    def search_events(self, user_id: int, keyword: Optional[str] = None, 
                     start_date: Optional[date] = None, end_date: Optional[date] = None,
                     role: Optional[str] = None, location: Optional[str] = None,
                     attendance_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Advanced search for events with multiple filter options"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # Build dynamic query
            query = """
                SELECT DISTINCT e.* 
                FROM events e
                INNER JOIN event_attendees ea ON e.id = ea.event_id
                WHERE ea.user_id = %s
            """
            params = [user_id]
            
            # Filter by role (organizer or attendee)
            if role:
                query += " AND ea.role = %s"
                params.append(role)
            
            # Filter by attendance status
            if attendance_status:
                query += " AND ea.attendance_status = %s"
                params.append(attendance_status)
            
            # Filter by keyword (search in title and description)
            if keyword:
                query += " AND (e.title LIKE %s OR e.description LIKE %s)"
                keyword_pattern = f"%{keyword}%"
                params.extend([keyword_pattern, keyword_pattern])
            
            # Filter by date range
            if start_date:
                query += " AND e.date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND e.date <= %s"
                params.append(end_date)
            
            # Filter by location
            if location:
                query += " AND e.location LIKE %s"
                params.append(f"%{location}%")
            
            query += " ORDER BY e.date DESC, e.created_at DESC"
            
            cursor.execute(query, tuple(params))
            events = cursor.fetchall() or []
            
            # Convert timedelta to time for each event
            for event in events:
                if 'time' in event:
                    event['time'] = convert_timedelta_to_time(event['time'])
            
            return list(events)
        except mysql.connector.Error as err:
            logger.error(f"Database error searching events: {err}")
            raise DatabaseException(f"Failed to search events: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error searching events: {str(e)}")
            raise DatabaseException("Failed to search events")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)


