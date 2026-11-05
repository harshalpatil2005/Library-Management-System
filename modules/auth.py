# modules/auth.py

from modules.database_manager import DatabaseManager
from modules.activity_log import log_activity # New import

def login_user(username, password):
    """
    Checks if a user exists with the given username and password.
    Returns the user data if successful, otherwise None.
    """
    db = DatabaseManager()
    db.connect()

    query = "SELECT User_ID, Name, Role FROM User WHERE Username = %s AND Password = %s"
    user_data = db.fetch_one(query, (username, password))

    db.close()

    if user_data:
        log_activity(user_data['User_ID'], f"Logged in to the system.") # <-- New line
        return user_data
    else:
        return None

def get_user_role(user_id):
    """
    Retrieves the role of a user from the database.
    """
    db = DatabaseManager()
    db.connect()

    query = "SELECT Role FROM User WHERE User_ID = %s"
    user_role = db.fetch_one(query, (user_id,))

    db.close()

    if user_role:
        return user_role['Role']
    else:
        return None