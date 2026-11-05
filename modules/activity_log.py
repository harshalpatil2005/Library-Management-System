# modules/activity_log.py

from modules.database_manager import DatabaseManager
import datetime


def log_activity(user_id, action):
    """Logs an activity to the database."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "INSERT INTO Activity_Log (User_ID, Date_Time, Action) VALUES (%s, %s, %s)"
        db.execute_query(query, (user_id, datetime.datetime.now(), action))
        return True
    except Exception as e:
        print(f"Error logging activity: {e}")
        return False
    finally:
        db.close()


def get_all_logs():
    """Retrieves all activity logs from the database."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "SELECT l.Log_ID, u.Name as User_Name, l.Date_Time, l.Action FROM Activity_Log l JOIN User u ON l.User_ID = u.User_ID ORDER BY l.Date_Time DESC"
        logs = db.fetch_all(query)  # <-- CHANGED to use db.fetch_all()
        return logs
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []
    finally:
        db.close()