from modules.database_manager import DatabaseManager
from modules.activity_log import log_activity  # Ensure this is imported for logging
import datetime

# Fine constants
OVERDUE_FINE_PER_DAY = 0.50
DAMAGED_BOOK_FINE = 5.00


def get_issue_bill_data(issue_id):
    """
    Retrieves all necessary data to generate an issue bill.
    """
    db = DatabaseManager()
    db.connect()
    try:
        query = """
        SELECT 
            ir.Issue_ID,
            ir.Issue_Date,
            ir.Due_Date,
            u.Name AS MemberName,
            u.User_ID AS MemberID,
            b.Title AS BookTitle,
            b.Author AS BookAuthor,
            b.Book_ID
        FROM Issue_Record ir
        JOIN User u ON ir.User_ID = u.User_ID
        JOIN Book b ON ir.Book_ID = b.Book_ID
        WHERE ir.Issue_ID = %s
        """
        bill_data = db.fetch_one(query, (issue_id,))
        return bill_data
    except Exception as e:
        print(f"Error fetching bill data: {e}")
        return None
    finally:
        db.close()


def calculate_fine(issue_id):
    """
    Calculates the total fine for an issued book (overdue + damage).
    Returns: (total_fine, overdue_fine)
    """
    db = DatabaseManager()
    db.connect()
    overdue_fine = 0.0
    total_fine = 0.0
    try:
        query = "SELECT Due_Date, Return_Date, Damage_Fine FROM Issue_Record WHERE Issue_ID = %s"
        record = db.fetch_one(query, (issue_id,))
        if not record:
            return 0.0, 0.0

        due_date = record['Due_Date']
        if isinstance(due_date, str):
            # Assumes format is like 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'
            due_date = datetime.datetime.strptime(due_date.split()[0], '%Y-%m-%d').date()

        return_date = record['Return_Date']
        if return_date and isinstance(return_date, str):
            return_date = datetime.datetime.strptime(return_date.split()[0], '%Y-%m-%d').date()

        # Damage_Fine is stored in the Issue_Record on return
        damage_fine = record['Damage_Fine'] if record['Damage_Fine'] is not None else 0.0

        # Calculate Overdue Fine only if the book has been returned
        if return_date and return_date > due_date:
            delay = (return_date - due_date).days
            overdue_fine = delay * OVERDUE_FINE_PER_DAY

        total_fine = overdue_fine + damage_fine
        return total_fine, overdue_fine
    except Exception as e:
        print(f"Error calculating fine for issue ID {issue_id}: {e}")
        return 0.0, 0.0
    finally:
        db.close()


def finalize_return_billing(member_id, issue_id, staff_id, fine_amount):
    """
    Creates billing record for a returned book and logs the activity.
    Marks Paid_Status 'Paid' immediately for demo purposes based on your UI function 'pay_fine'.
    """
    db = DatabaseManager()
    db.connect()
    bill_id = None
    try:
        # CRITICAL FIX: Changed Total_Fine -> Amount and Generated_Date -> Transaction_Date
        # to match the Billing table schema from create_tables.sql
        transaction_date = datetime.date.today()
        paid_status = 'Paid'  # Assumes fine is paid immediately in the UI function

        # NOTE: Added Issue_ID into the Billing table for better tracking,
        # but the table definition in create_tables.sql doesn't show it.
        # We must insert into the columns that exist: User_ID, Amount, Transaction_Date, Paid_Status (assuming you added Paid_Status)
        insert_query = """
        INSERT INTO Billing (User_ID, Amount, Transaction_Date, Description, Paid_Status)
        VALUES (%s, %s, %s, %s, %s)
        """
        # Added a Description field to store Issue_ID reference since Billing table only has:
        # Bill_ID, Transaction_Date, Amount, Description, User_ID (based on create_tables.sql)
        description = f"Fine for Issue ID {issue_id}"
        db.execute_query(insert_query, (member_id, fine_amount, transaction_date, description, paid_status))
        bill_id = db.get_last_row_id()

        log_activity(staff_id,
                     f"Recorded and paid bill (ID: {bill_id}) for Issue ID {issue_id}. Fine: ${fine_amount:.2f}")

        return True, "Bill recorded successfully."
    except Exception as e:
        print(f"Error creating billing record: {e}")
        return False, f"Database Error: Could not record bill. {e}"
    finally:
        db.close()


def get_member_balance(member_id):
    """
    Total pending fines for a member.
    """
    db = DatabaseManager()
    db.connect()
    try:
        # FINAL CRITICAL FIX: Ensure query correctly targets the 'Amount' column
        # and explicitly names the result as Total_Balance for the Python dictionary key.
        query = "SELECT SUM(Amount) AS Total_Balance FROM Billing WHERE User_ID=%s AND Paid_Status='Pending'"
        result = db.fetch_one(query, (member_id,))
        if result and result['Total_Balance'] is not None:
            # We must cast the decimal result to a float for Python calculations
            return float(result['Total_Balance'])
        return 0.0
    except Exception as e:
        print(f"Error calculating member balance: {e}")
        return 0.0
    finally:
        db.close()
