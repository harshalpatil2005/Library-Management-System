# modules/overdue_alerts.py

from .database_manager import DatabaseManager
import datetime

# Attempt to import FINE_PER_DAY. If it fails (e.g., billing.py is missing),
# we default to a safe value to prevent a crash.
try:
    from .billing import FINE_PER_DAY
except ImportError:
    FINE_PER_DAY = 1.00  # Default fine rate


def get_overdue_count():
    """
    Fetches the total count of overdue books from the database.

    :return: The number of overdue books as an integer.
    """
    db = DatabaseManager()
    db.connect()

    overdue_count = 0
    try:
        query = """
        SELECT COUNT(*) AS overdue_count
        FROM Issue_Record
        WHERE Due_Date < CURDATE() AND Return_Date IS NULL
        """
        result = db.fetch_one(query)
        # Safely extract count, defaulting to 0 if no result or key is missing
        overdue_count = result.get('overdue_count', 0) if result else 0
    except Exception as e:
        print(f"Error fetching overdue count: {e}")
    finally:
        db.close()

    return overdue_count


def get_all_overdue_books():
    """
    Retrieves all books currently issued and past their due date across all members.
    Includes calculated overdue fine amount.
    """
    db = DatabaseManager()
    db.connect()
    try:
        today = datetime.date.today()

        # Calculate overdue days and fine directly in the query
        query = f"""
        SELECT 
            ir.Issue_ID, 
            ir.Book_ID,
            b.Title,
            ir.User_ID,
            u.Name AS Member_Name,  -- fixed: use Name field instead of First_Name/Last_Name
            ir.Issue_Date, 
            ir.Due_Date,
            DATEDIFF(%s, ir.Due_Date) AS Overdue_Days,
            DATEDIFF(%s, ir.Due_Date) * {FINE_PER_DAY} AS Overdue_Fine
        FROM Issue_Record ir
        JOIN Book b ON ir.Book_ID = b.Book_ID
        JOIN User u ON ir.User_ID = u.User_ID
        WHERE ir.Return_Date IS NULL 
          AND ir.Due_Date < %s
        ORDER BY ir.Due_Date ASC
        """
        # Pass today's date three times
        overdue_books = db.fetch_all(query, (today, today, today))
        return overdue_books
    except Exception as e:
        print(f"Error fetching all overdue books: {e}")
        return []
    finally:
        db.close()


def get_ready_reservations():
    """
    Retrieves all reservations that are marked 'Ready' for pickup by a member.
    """
    db = DatabaseManager()
    db.connect()
    try:
        query = """
        SELECT 
            r.Reservation_ID,
            r.Book_ID,
            b.Title,
            r.User_ID,
            u.Name AS Member_Name,  -- fixed: use Name instead of First_Name/Last_Name
            r.Reservation_Date
        FROM Reservation r
        JOIN Book b ON r.Book_ID = b.Book_ID
        JOIN User u ON r.User_ID = u.User_ID
        WHERE r.Status = 'Ready'
        ORDER BY r.Reservation_Date ASC
        """
        ready_reservations = db.fetch_all(query)
        return ready_reservations
    except Exception as e:
        print(f"Error fetching ready reservations: {e}")
        return []
    finally:
        db.close()
