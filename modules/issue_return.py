# module issue_return.py
from modules.database_manager import DatabaseManager
from modules.activity_log import log_activity
import datetime

# This fine amount should match the one defined in ui/issue_return.py
DAMAGED_BOOK_FINE = 5.00


def get_member_by_id(member_id):
    """Retrieves a member's details by their User_ID."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "SELECT * FROM User WHERE User_ID = %s"
        member = db.fetch_one(query, (member_id,))
        return member
    except Exception as e:
        print(f"Error fetching member: {e}")
        return None
    finally:
        db.close()


def get_book_by_id(book_id):
    """Retrieves a book's details by its Book_ID."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "SELECT * FROM Book WHERE Book_ID = %s"
        book = db.fetch_one(query, (book_id,))
        return book
    except Exception as e:
        print(f"Error fetching book: {e}")
        return None
    finally:
        db.close()


# --- NEW: Reservation Functions ---

def reserve_book(book_id, user_id):
    """
    Creates a new reservation for a book.
    """
    db = DatabaseManager()
    db.connect()
    try:
        # Check if the member already has a pending reservation for this book
        query = "SELECT COUNT(*) FROM Reservation WHERE Book_ID = %s AND User_ID = %s AND Status = 'Pending'"
        count = db.fetch_one(query, (book_id, user_id))['COUNT(*)']
        if count > 0:
            return False, "You already have a pending reservation for this book."

        reservation_date = datetime.date.today()
        status = 'Pending'

        insert_query = "INSERT INTO Reservation (Book_ID, User_ID, Reservation_Date, Status) VALUES (%s, %s, %s, %s)"
        db.execute_query(insert_query, (book_id, user_id, reservation_date, status))

        log_activity(user_id, f"Reserved book ID {book_id} for user ID {user_id}.")
        return True, "Book reserved successfully. You will be notified when it is available."
    except Exception as e:
        print(f"Error reserving book: {e}")
        return False, f"An error occurred: {e}"
    finally:
        db.close()


def check_for_reservations(book_id):
    """
    Checks for and updates the oldest pending reservation for a book.
    """
    db = DatabaseManager()
    db.connect()
    try:
        # Find the oldest pending reservation for this book
        query = """
        SELECT Reservation_ID, User_ID
        FROM Reservation
        WHERE Book_ID = %s AND Status = 'Pending'
        ORDER BY Reservation_Date ASC
        LIMIT 1
        """
        reservation = db.fetch_one(query, (book_id,))

        if reservation:
            # Update the reservation status to 'Ready'
            update_query = "UPDATE Reservation SET Status = 'Ready' WHERE Reservation_ID = %s"
            db.execute_query(update_query, (reservation['Reservation_ID'],))

            # Log the notification (in a real app, this would be an email/SMS)
            log_activity(1,
                         f"Book ID {book_id} is now ready for pickup by user ID {reservation['User_ID']} based on reservation ID {reservation['Reservation_ID']}.")
            print(f"Notification: Book {book_id} is now available for pickup by member {reservation['User_ID']}.")
            return True, "Reservation updated and member notified."
        return False, "No pending reservations for this book."
    except Exception as e:
        print(f"Error checking for reservations: {e}")
        return False, f"An error occurred: {e}"
    finally:
        db.close()


# --- MODIFIED: return_book function ---

def return_book(user_id, issue_id, is_damaged):
    """
    Returns an issued book, updates the book quantity, and applies a fine if damaged.
    Also handles pending reservations.
    """
    db = DatabaseManager()
    db.connect()
    try:
        # Get the issue record to find the book_id
        fetch_issue_query = "SELECT Book_ID FROM Issue_Record WHERE Issue_ID = %s AND Return_Date IS NULL"
        issue_record = db.fetch_one(fetch_issue_query, (issue_id,))

        if not issue_record:
            return False, "Issue record not found or book already returned."

        book_id = issue_record['Book_ID']
        return_date = datetime.date.today()

        fine = DAMAGED_BOOK_FINE if is_damaged else 0.0

        # Update the Issue_Record with the return date and damage fine
        return_query = "UPDATE Issue_Record SET Return_Date = %s, Damage_Fine = %s WHERE Issue_ID = %s"
        db.execute_query(return_query, (return_date, fine, issue_id))

        # Check for and update the oldest pending reservation for this book
        has_reservations, _ = check_for_reservations(book_id)

        if not has_reservations:
            # If no reservations exist, increase the book quantity by 1
            update_book_query = "UPDATE Book SET Quantity = Quantity + 1 WHERE Book_ID = %s"
            db.execute_query(update_book_query, (book_id,))
        else:
            # If a reservation exists, the book is held and its quantity remains low.
            # It's not available for new checkouts yet.
            pass

        # Log the activity
        action_message = f"Returned book ID {book_id} from issue ID {issue_id}."
        if is_damaged:
            action_message += f" A fine of ${fine:.2f} was applied for damage."
        log_activity(user_id, action_message)

        return True, "Book returned successfully."
    except Exception as e:
        print(f"Error returning book: {e}")
        return False, f"An error occurred: {e}"
    finally:
        db.close()


# --- Unchanged functions below ---

def issue_book(user_id, book_id, member_id):
    """Issues a book to a member and updates the book quantity."""
    db = DatabaseManager()
    db.connect()
    try:
        # Check if book is available
        book = get_book_by_id(book_id)
        if not book or book['Quantity'] <= 0:
            return False, "Book is not available."

        # Define dates
        issue_date = datetime.date.today()
        due_date = issue_date + datetime.timedelta(days=14)  # Example: 14-day loan period

        # Insert into Issue_Record
        issue_query = "INSERT INTO Issue_Record (Issue_Date, Due_Date, User_ID, Book_ID) VALUES (%s, %s, %s, %s)"
        db.execute_query(issue_query, (issue_date, due_date, member_id, book_id))

        # Update book quantity
        update_book_query = "UPDATE Book SET Quantity = Quantity - 1 WHERE Book_ID = %s"
        db.execute_query(update_book_query, (book_id,))

        # Log the activity
        log_activity(user_id, f"Issued book ID {book_id} to user ID {member_id}.")

        return True, "Book issued successfully."
    except Exception as e:
        print(f"Error issuing book: {e}")
        return False, f"An error occurred: {e}"
    finally:
        db.close()


def get_issued_books_by_member(member_id):
    """Retrieves all books currently issued to a specific member."""
    db = DatabaseManager()
    db.connect()
    try:
        query = """
        SELECT ir.Issue_ID, b.Title, ir.Issue_Date, ir.Due_Date
        FROM Issue_Record ir
        JOIN Book b ON ir.Book_ID = b.Book_ID
        WHERE ir.User_ID = %s AND ir.Return_Date IS NULL
        """
        issued_books = db.fetch_all(query, (member_id,))
        return issued_books
    except Exception as e:
        print(f"Error fetching issued books: {e}")
        return []
    finally:
        db.close()