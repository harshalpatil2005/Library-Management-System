from datetime import datetime


def print_transaction_bill(data):
    """
    Prints a formatted transaction bill to the console.

    Args:
        data (dict): Dictionary containing all necessary transaction details
                     (e.g., Book_ID, Member_ID, Date, Fine_Amount, etc.)
    """

    # 1. Prepare Data by safely getting values from the dictionary
    txn_id = data.get('Transaction_ID', 'N/A')
    txn_type = data.get('Transaction_Type', 'N/A').upper()

    # Dates
    txn_date_str = data.get('Transaction_Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    due_date_str = data.get('Due_Date', 'N/A')

    # Entities
    book_id = data.get('Book_ID', 'N/A')
    book_title = data.get('Book_Title', 'Unknown Title')
    member_id = data.get('Member_ID', 'N/A')
    member_name = data.get('Member_Name', 'Unknown Member')

    # Financials
    fine_amount = data.get('Fine_Amount', 0.0)
    staff_user = data.get('Staff_User', 'N/A')

    # 2. Format and Print Output (50 characters wide)
    print("-" * 50)
    print(f"| {'LIBRARY MANAGEMENT SYSTEM - RECEIPT':^48} |")
    print("-" * 50)
    print(f"| Transaction ID: {txn_id:<32} |")
    print(f"| Transaction Type: {txn_type:<30} |")
    print("-" * 50)

    print(f"| Book: {book_title[:42]:<42} |")
    print(f"| Book ID: {book_id:<41} |")

    if txn_type == 'ISSUE':
        print(f"| Issue Date: {txn_date_str:<38} |")
        print(f"| Due Date: {due_date_str:<40} |")
    elif txn_type == 'RETURN':
        print(f"| Return Date: {txn_date_str:<37} |")

    print("-" * 50)
    print(f"| Member Name: {member_name[:37]:<37} |")
    print(f"| Member ID: {member_id:<39} |")
    print("-" * 50)

    # Fine details section
    if fine_amount > 0:
        fine_text = f"*** TOTAL FINE DUE: ${fine_amount:.2f} ***"
        print(f"| {fine_text:^48} |")
        print("-" * 50)
    else:
        print(f"| TOTAL DUE: $0.00 |")
        print("-" * 50)

    print(f"| Processed by: {staff_user:<34} |")
    print(f"| Printed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<36} |")
    print("-" * 50)
    print("\n")
