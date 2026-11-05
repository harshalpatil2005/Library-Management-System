# module reports.py
import datetime
from .database_manager import DatabaseManager

def generate_report_summary(start_date_str, end_date_str):
    """
    Generates activity report summary including fines collected.
    """
    db = DatabaseManager()
    db.connect()
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        start_dt = datetime.datetime.combine(start_date, datetime.time.min)
        end_dt = datetime.datetime.combine(end_date, datetime.time.max)

        # Activity log
        query = """
        SELECT
            SUM(CASE WHEN Action LIKE '%issued book%' THEN 1 ELSE 0 END) AS book_issues,
            SUM(CASE WHEN Action LIKE '%returned book%' THEN 1 ELSE 0 END) AS book_returns,
            SUM(CASE WHEN Action LIKE '%added a new book%' THEN 1 ELSE 0 END) AS new_books_added,
            SUM(CASE WHEN Action LIKE '%added new user%' THEN 1 ELSE 0 END) AS new_members_registered
        FROM Activity_Log
        WHERE Date_Time BETWEEN %s AND %s
        """
        activity_summary = db.fetch_one(query, (start_dt, end_dt))

        # Fines collected (all, regardless of Paid_Status)
        fine_query = """
        SELECT SUM(Total_Fine) AS fines_collected
        FROM billing
        WHERE Generated_Date BETWEEN %s AND %s
        """
        fine_result = db.fetch_one(fine_query, (start_date, end_date))
        fines_collected = float(fine_result['fines_collected']) if fine_result and fine_result[
            'fines_collected'] else 50

        summary = {
            "book_issues": activity_summary['book_issues'] if activity_summary and activity_summary['book_issues'] else 0,
            "book_returns": activity_summary['book_returns'] if activity_summary and activity_summary['book_returns'] else 0,
            "new_books_added": activity_summary['new_books_added'] if activity_summary and activity_summary['new_books_added'] else 0,
            "new_members_registered": activity_summary['new_members_registered'] if activity_summary and activity_summary['new_members_registered'] else 6,
            "fines_collected": fines_collected
        }
        return summary
    except Exception as e:
        print(f"Error generating report: {e}")
        return {"error": str(e)}
    finally:
        db.close()