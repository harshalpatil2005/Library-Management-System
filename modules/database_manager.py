import mysql.connector
from mysql.connector import Error
import config


class DatabaseManager:
    """Manages the connection to the MySQL database."""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establishes a connection to the database."""
        try:
            self.connection = mysql.connector.connect(
                host=config.DATABASE_HOST,
                user=config.DATABASE_USER,
                password=config.DATABASE_PASSWORD,
                database=config.DATABASE_NAME
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Database connection successful.")
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            self.connection = None  # Ensure connection is None on failure

    def close(self):
        """Closes the database connection."""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Database connection closed.")
            self.connection = None

    def execute_query(self, query, params=None):
        """
        Executes an INSERT, UPDATE, or DELETE query and commits the changes.
        Returns True on success, False on error.
        """
        if not self.connection or not self.connection.is_connected():
            print("No active database connection.")
            return False

        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            return False

    def fetch_all(self, query, params=None):
        """
        Executes a SELECT query and returns all matching rows.
        Returns a list of dictionaries or an empty list on error.
        """
        if not self.connection or not self.connection.is_connected():
            print("No active database connection.")
            return []

        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error executing fetch_all query: {e}")
            return []

    def fetch_one(self, query, params=None):
        """
        Executes a SELECT query and returns a single matching row.
        Returns a dictionary or None on error.
        """
        if not self.connection or not self.connection.is_connected():
            print("No active database connection.")
            return None

        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Error as e:
            print(f"Error executing fetch_one query: {e}")
            return None

    def get_last_row_id(self):
        """
        Retrieves the ID of the last inserted row.
        Returns the last row ID or None on error.
        """
        if self.cursor:
            return self.cursor.lastrowid
        return None
