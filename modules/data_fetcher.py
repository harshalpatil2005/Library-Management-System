# This file requires the DatabaseManager class from your existing database_manager module.
from modules.database_manager import DatabaseManager

# ------------------------- FETCH MEMBER -------------------------
def get_member_by_id(member_id):
    """
    Fetches member details by User_ID for display in the UI (e.g., in the Issue tab).
    Returns a dictionary {'User_ID', 'Name', 'Type', ...} or None.
    """
    db = DatabaseManager()
    db.connect()
    try:
        # Searches the Member table
        query = "SELECT User_ID, Name, Member_Type AS Type, Contact FROM Member WHERE User_ID=%s"
        member_data = db.fetch_one(query, (member_id,))
        return member_data
    except Exception as e:
        print(f"Database Error fetching member {member_id}: {e}")
        return None
    finally:
        db.close()

# ------------------------- FETCH BOOK -------------------------
def get_book_by_id(book_id):
    """
    Fetches book details by Book_ID for display (e.g., status check).
    Returns a dictionary {'Book_ID', 'Title', 'Status', ...} or None.
    """
    db = DatabaseManager()
    db.connect()
    try:
        # Searches the Book table
        query = "SELECT Book_ID, Title, Author, Status FROM Book WHERE Book_ID=%s"
        book_data = db.fetch_one(query, (book_id,))
        return book_data
    except Exception as e:
        print(f"Database Error fetching book {book_id}: {e}")
        return None
    finally:
        db.close()
