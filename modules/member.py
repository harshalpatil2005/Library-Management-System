# modules/member.py

from modules.database_manager import DatabaseManager
from modules.activity_log import log_activity


def add_member(user_id, name, username, password, role, contact, email, user_type):
    """Inserts a new member record into the User table and logs the activity."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "INSERT INTO User (Name, Username, Password, Role, Contact, Email, User_Type) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        db.execute_query(query, (name, username, password, role, contact, email, user_type))

        log_activity(user_id, f"Added a new user: '{name}' with role '{role}'.")

        return True
    except Exception as e:
        print(f"Error adding member: {e}")
        return False
    finally:
        db.close()


def get_all_members():
    """Retrieves all users with 'Member' role from the database."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "SELECT User_ID, Name, Username, Role, Contact, Email, User_Type FROM User WHERE Role='Member'"
        members = db.fetch_all(query)
        return members
    except Exception as e:
        print(f"Error fetching members: {e}")
        return []
    finally:
        db.close()


def get_all_staff():
    """Fetches all users with 'Librarian' or 'Staff' role from the database."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "SELECT User_ID, Name, Username, Role, Contact, Email FROM User WHERE Role IN ('Librarian', 'Staff')"
        staff = db.fetch_all(query)
        return staff
    except Exception as e:
        print(f"Error fetching staff members: {e}")
        return []
    finally:
        db.close()


def add_staff(admin_id, name, username, password, role, contact, email):
    """Adds a new staff member to the database."""
    db = DatabaseManager()
    db.connect()
    try:
        if role not in ['Librarian', 'Staff']:
            return False

        # Staff don't have a 'user_type', so it's set to NULL
        query = "INSERT INTO User (Name, Username, Password, Role, Contact, Email, User_Type) VALUES (%s, %s, %s, %s, %s, %s, NULL)"
        db.execute_query(query, (name, username, password, role, contact, email))

        log_activity(admin_id, f"Added a new staff member: '{name}' with role '{role}'.")
        return True
    except Exception as e:
        print(f"Error adding staff member: {e}")
        return False
    finally:
        db.close()


def update_staff(admin_id, staff_id, name, username, password, role, contact, email):
    """Updates an existing staff member record and logs the activity."""
    db = DatabaseManager()
    db.connect()
    try:
        if password:
            query = "UPDATE User SET Name=%s, Username=%s, Password=%s, Role=%s, Contact=%s, Email=%s WHERE User_ID=%s"
            db.execute_query(query, (name, username, password, role, contact, email, staff_id))
        else:
            query = "UPDATE User SET Name=%s, Username=%s, Role=%s, Contact=%s, Email=%s WHERE User_ID=%s"
            db.execute_query(query, (name, username, role, contact, email, staff_id))

        log_activity(admin_id, f"Updated staff member ID {staff_id}: '{name}'.")
        return True
    except Exception as e:
        print(f"Error updating staff member: {e}")
        return False
    finally:
        db.close()


def delete_staff(admin_id, staff_id):
    """Deletes a staff member from the User table and logs the activity."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "DELETE FROM User WHERE User_ID=%s"
        db.execute_query(query, (staff_id,))

        log_activity(admin_id, f"Deleted staff member with ID {staff_id}.")
        return True
    except Exception as e:
        print(f"Error deleting staff member: {e}")
        return False
    finally:
        db.close()


def update_member(admin_id, member_id, name, username, password, role, contact, email, user_type):
    """Updates an existing member record in the User table and logs the activity."""
    db = DatabaseManager()
    db.connect()
    try:
        if password:
            query = "UPDATE User SET Name=%s, Username=%s, Password=%s, Role=%s, Contact=%s, Email=%s, User_Type=%s WHERE User_ID=%s"
            db.execute_query(query, (name, username, password, role, contact, email, user_type, member_id))
        else:
            query = "UPDATE User SET Name=%s, Username=%s, Role=%s, Contact=%s, Email=%s, User_Type=%s WHERE User_ID=%s"
            db.execute_query(query, (name, username, role, contact, email, user_type, member_id))

        log_activity(admin_id, f"Updated user ID {member_id}: '{name}'.")
        return True
    except Exception as e:
        print(f"Error updating member: {e}")
        return False
    finally:
        db.close()


def delete_member(admin_id, member_id):
    """Deletes a member from the User table and logs the activity."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "DELETE FROM User WHERE User_ID=%s"
        db.execute_query(query, (member_id,))

        log_activity(admin_id, f"Deleted user with ID {member_id}.")

        return True
    except Exception as e:
        print(f"Error deleting member: {e}")
        return False
    finally:
        db.close()