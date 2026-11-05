from modules.database_manager import DatabaseManager
from modules.activity_log import log_activity


def add_book(user_id, title, author, language, release_date, quantity, genre):
    """Inserts a new book into the database and logs the activity."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "INSERT INTO Book (Title, Author, Language, Release_Date, Quantity, Genre) VALUES (%s, %s, %s, %s, %s, %s)"
        db.execute_query(query, (title, author, language, release_date, quantity, genre))

        # Log the activity
        log_activity(user_id, f"Added a new book: '{title}' by {author}.")

        return True
    except Exception as e:
        print(f"Error adding book: {e}")
        return False
    finally:
        db.close()


def get_all_books():
    """Retrieves all book records from the database."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "SELECT Book_ID, Title, Author, Language, Release_Date, Quantity, Genre FROM Book"
        books = db.fetch_all(query)
        return books
    except Exception as e:
        print(f"Error fetching books: {e}")
        return []
    finally:
        db.close()


def update_book(user_id, book_id, title, author, language, release_date, quantity, genre):
    """Updates an existing book record and logs the activity."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "UPDATE Book SET Title=%s, Author=%s, Language=%s, Release_Date=%s, Quantity=%s, Genre=%s WHERE Book_ID=%s"
        db.execute_query(query, (title, author, language, release_date, quantity, genre, book_id))

        # Log the activity
        log_activity(user_id, f"Updated book ID {book_id}: '{title}'.")

        return True
    except Exception as e:
        print(f"Error updating book: {e}")
        return False
    finally:
        db.close()


def delete_book(user_id, book_id):
    """Deletes a book from the database and logs the activity."""
    db = DatabaseManager()
    db.connect()
    try:
        query = "DELETE FROM Book WHERE Book_ID=%s"
        db.execute_query(query, (book_id,))

        # Log the activity
        log_activity(user_id, f"Deleted book with ID {book_id}.")

        return True
    except Exception as e:
        print(f"Error deleting book: {e}")
        return False
    finally:
        db.close()


def search_books(criteria):
    """Searches for books based on title or author."""
    db = DatabaseManager()
    db.connect()
    try:
        search_term = f"%{criteria}%"
        query = "SELECT * FROM Book WHERE Title LIKE %s OR Author LIKE %s"
        books = db.fetch_all(query, (search_term, search_term))
        return books
    except Exception as e:
        print(f"Error searching books: {e}")
        return []
    finally:
        db.close()


def get_book_counts():
    """
    Returns the total count of unique book titles and the total count of all book items.
    """
    db = DatabaseManager()
    db.connect()
    try:
        # Count the number of unique book titles
        unique_titles_query = "SELECT COUNT(Book_ID) AS Total_Titles FROM Book"
        total_titles = db.fetch_one(unique_titles_query)['Total_Titles']

        # Count the total number of all book items (sum of quantities)
        all_books_query = "SELECT SUM(Quantity) AS Total_Books FROM Book"
        total_books = db.fetch_one(all_books_query)['Total_Books']

        return total_titles, total_books if total_books else 0
    except Exception as e:
        print(f"Error fetching book counts: {e}")
        return 0, 0
    finally:
        db.close()