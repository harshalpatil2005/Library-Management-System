import tkinter as tk
from tkinter import ttk, messagebox

# We need to import the DateEntry widget for the calendar functionality
# NOTE: You must install this library: pip install tkcalendar
try:
    from tkcalendar import DateEntry
except ImportError:
    # Define a placeholder if tkcalendar is not installed, but inform the user
    class DateEntry(tk.Entry):
        def __init__(self, master=None, **kw):
            super().__init__(master, **kw)
            self.insert(0, "YYYY-MM-DD")


    # This messagebox is aggressive, but ensures the user knows the dependency is missing
    messagebox.showerror("Dependency Error",
                         "The 'tkcalendar' library is missing. Please install it using: pip install tkcalendar")

from modules import book
import re  # Import for regular expression validation

# --- UI Color Scheme (must be defined or imported) ---
MAIN_CONTENT_BG = "#ECF0F1"
BUTTON_BG = "#3498DB"
BUTTON_FG = "#FFFFFF"
FORM_LABEL_BG = MAIN_CONTENT_BG
ERROR_FG = "#CC3333"  # Define a color for error visibility


class BookManagementWindow:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        # Safely access user_id from the top-level window's current_user attribute
        try:
            self.user_id = self.parent_frame.winfo_toplevel().current_user['User_ID']
        except AttributeError:
            self.user_id = "STAFF_ID_UNKNOWN"
            messagebox.showwarning("User Context", "Could not retrieve User ID. Using placeholder.")

        self.create_widgets()
        self.load_books()
        self.update_totals()

    def create_widgets(self):
        self.main_content_frame = tk.Frame(self.parent_frame, bg=MAIN_CONTENT_BG)
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(1, weight=3)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(1, weight=0)

        # Frame for the form
        self.form_frame = tk.LabelFrame(self.main_content_frame, text="Manage Books", bg=MAIN_CONTENT_BG, padx=15,
                                        pady=15)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Labels and Entry fields
        row_num = 0
        tk.Label(self.form_frame, text="Title:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_title = tk.Entry(self.form_frame)
        self.entry_title.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Author:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_author = tk.Entry(self.form_frame)
        self.entry_author.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Language:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_language = tk.Entry(self.form_frame)
        self.entry_language.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        # --- RELEASE DATE FIELD (CHANGED TO CALENDAR WIDGET) ---
        tk.Label(self.form_frame, text="Release Date:", bg=FORM_LABEL_BG).grid(row=row_num, column=0,
                                                                               sticky="w", pady=5)
        # Use DateEntry from tkcalendar
        self.entry_release_date = DateEntry(self.form_frame, width=12, background=BUTTON_BG,
                                            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.entry_release_date.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Quantity:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_quantity = tk.Entry(self.form_frame)
        self.entry_quantity.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Genre:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_genre = tk.Entry(self.form_frame)
        self.entry_genre.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        # Buttons for actions
        button_style = {"bg": BUTTON_BG, "fg": BUTTON_FG, "font": ("Arial", 10, "bold"), "relief": "flat"}

        button_frame = tk.Frame(self.form_frame, bg=MAIN_CONTENT_BG)
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Update button commands to use validated versions
        self.button_add = tk.Button(button_frame, text="Add Book", command=self.add_book_validated, **button_style)
        self.button_add.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        self.button_update = tk.Button(button_frame, text="Update Book", command=self.update_book_validated,
                                       **button_style)
        self.button_update.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        self.button_delete = tk.Button(button_frame, text="Delete Book", command=self.delete_book_validated,
                                       **button_style)
        self.button_delete.grid(row=1, column=0, pady=5, padx=5, sticky="ew")

        self.button_clear = tk.Button(button_frame, text="Clear Form", command=self.clear_form, **button_style)
        self.button_clear.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        self.form_frame.grid_columnconfigure(1, weight=1)

        # Treeview to display books
        self.books_tree_frame = tk.LabelFrame(self.main_content_frame, text="Book List", bg=MAIN_CONTENT_BG, padx=10,
                                              pady=10)
        self.books_tree_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.books_tree_frame.grid_columnconfigure(0, weight=1)
        self.books_tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("Book_ID", "Title", "Author", "Language", "Release_Date", "Quantity", "Genre")
        self.books_tree = ttk.Treeview(self.books_tree_frame, columns=columns, show="headings")

        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100, anchor="center")

        self.books_tree.grid(row=0, column=0, sticky="nsew")
        self.books_tree.bind("<ButtonRelease-1>", self.select_book)

        scrollbar = ttk.Scrollbar(self.books_tree_frame, orient="vertical", command=self.books_tree.yview)
        self.books_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Total Counts Frame (Unchanged) ---
        self.totals_frame = tk.Frame(self.main_content_frame, bg=MAIN_CONTENT_BG)
        self.totals_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.totals_frame.columnconfigure(0, weight=1)
        self.totals_frame.columnconfigure(1, weight=1)

        self.total_unique_books_label = tk.Label(self.totals_frame, text="Total Unique Titles: 0",
                                                 font=("Arial", 12, "bold"), bg=MAIN_CONTENT_BG, anchor="w")
        self.total_unique_books_label.grid(row=0, column=0, sticky="w", padx=10)

        self.total_all_books_label = tk.Label(self.totals_frame, text="Total All Books: 0", font=("Arial", 12, "bold"),
                                              bg=MAIN_CONTENT_BG, anchor="e")
        self.total_all_books_label.grid(row=0, column=1, sticky="e", padx=10)

    # --- NEW VALIDATION METHOD ---
    def validate_book_input(self):
        """Validates all input fields based on strict type requirements."""

        # Get values. Note: DateEntry uses .get() which returns the formatted date string
        data = {
            'title': self.entry_title.get().strip(),
            'author': self.entry_author.get().strip(),
            'language': self.entry_language.get().strip(),
            'release_date': self.entry_release_date.get(),
            'quantity': self.entry_quantity.get().strip(),
            'genre': self.entry_genre.get().strip()
        }

        errors = []

        # 1. Title: Required, but content type is flexible (as requested)
        if not data['title']:
            errors.append("Title is required.")

        # 2. Author, Language, Genre: Must be non-empty and primarily contain letters, spaces, or hyphens
        # Allows common characters for names/genres/languages: letters, spaces, hyphens
        name_regex = r"^[a-zA-Z\s\-]+$"

        for field in ['author', 'language', 'genre']:
            value = data[field]
            if not value:
                errors.append(f"{field.capitalize()} is required.")
            elif not re.match(name_regex, value):
                errors.append(f"{field.capitalize()} must contain only letters, spaces, or hyphens.")

        # 3. Release Date: Must be selected (DateEntry ensures format)
        # We check if the field is empty or if it contains the default placeholder
        if not data['release_date'] or data['release_date'] == 'YYYY-MM-DD':
            errors.append("Release Date must be selected from the calendar.")

        # 4. Quantity: Must be a non-empty, positive integer
        try:
            quantity_val = data['quantity']
            if not quantity_val: raise ValueError("required")

            quantity_int = int(quantity_val)
            if quantity_int <= 0:
                errors.append("Quantity must be a positive whole number greater than 0.")
        except ValueError as e:
            if str(e) == "required":
                errors.append("Quantity is required.")
            else:
                errors.append("Quantity must be a valid whole number.")

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return None  # Return None if validation fails

        # Return validated data as a dictionary
        return data

    # --- MODIFIED CRUD METHODS TO USE VALIDATION ---
    def add_book_validated(self):
        """Adds a new book after validating the form data."""
        validated_data = self.validate_book_input()
        if validated_data is None:
            return

        # Extract data from the dictionary and ensure quantity is an integer
        title = validated_data['title']
        author = validated_data['author']
        language = validated_data['language']
        release_date = validated_data['release_date']
        quantity = int(validated_data['quantity'])
        genre = validated_data['genre']

        if book.add_book(self.user_id, title, author, language, release_date, quantity, genre):
            messagebox.showinfo("Success", "Book added successfully!")
            self.clear_form()
            self.load_books()
            self.update_totals()
        else:
            messagebox.showerror("Error", "Failed to add book.")

    def update_book_validated(self):
        """Updates the selected book after validating the form data."""
        selected_item = self.books_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a book to update.")
            return

        book_id = self.books_tree.item(selected_item, 'values')[0]

        validated_data = self.validate_book_input()
        if validated_data is None:
            return

        # Extract data from the dictionary and ensure quantity is an integer
        title = validated_data['title']
        author = validated_data['author']
        language = validated_data['language']
        release_date = validated_data['release_date']
        quantity = int(validated_data['quantity'])
        genre = validated_data['genre']

        if book.update_book(self.user_id, book_id, title, author, language, release_date, quantity, genre):
            messagebox.showinfo("Success", "Book updated successfully!")
            self.clear_form()
            self.load_books()
            self.update_totals()
        else:
            messagebox.showerror("Error", "Failed to update book.")

    def delete_book_validated(self):
        """Deletes the selected book."""
        selected_item = self.books_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a book to delete.")
            return

        book_id = self.books_tree.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete book ID {book_id}?"):
            if book.delete_book(self.user_id, book_id):
                messagebox.showinfo("Success", "Book deleted successfully.")
                self.clear_form()
                self.load_books()
                self.update_totals()
            else:
                messagebox.showerror("Error", "Failed to delete book.")

    # --- MODIFIED select_book METHOD ---
    def select_book(self, event):
        """Populates the form with data from the selected row."""
        selected_item = self.books_tree.focus()
        if selected_item:
            book_data = self.books_tree.item(selected_item, 'values')
            self.clear_form()
            self.entry_title.insert(0, book_data[1])
            self.entry_author.insert(0, book_data[2])
            self.entry_language.insert(0, book_data[3])

            # Handling for DateEntry widget
            try:
                # set_date is the correct way to update DateEntry
                self.entry_release_date.set_date(book_data[4])
            except AttributeError:
                # Fallback if DateEntry is placeholder
                self.entry_release_date.delete(0, tk.END)
                self.entry_release_date.insert(0, book_data[4])

            self.entry_quantity.insert(0, book_data[5])
            self.entry_genre.insert(0, book_data[6])

    # --- MODIFIED clear_form METHOD ---
    def clear_form(self):
        """Clears all entry fields in the form."""
        self.entry_title.delete(0, tk.END)
        self.entry_author.delete(0, tk.END)
        self.entry_language.delete(0, tk.END)

        # Handling for DateEntry widget
        try:
            # Setting date to None clears the selection
            self.entry_release_date.set_date(None)
        except AttributeError:
            self.entry_release_date.delete(0, tk.END)

        self.entry_quantity.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)

    # --- Remaining methods unchanged ---
    def load_books(self):
        """Loads all books from the database and displays them in the Treeview."""
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)

        books = book.get_all_books()
        if books:
            for book_item in books:
                self.books_tree.insert("", "end", values=(
                    book_item['Book_ID'],
                    book_item['Title'],
                    book_item['Author'],
                    book_item['Language'],
                    book_item['Release_Date'],
                    book_item['Quantity'],
                    book_item['Genre']
                ))

    def update_totals(self):
        """
        Fetches and updates the total book counts displayed at the bottom of the window.
        """
        total_titles, total_books = book.get_book_counts()
        self.total_unique_books_label.config(text=f"Total Unique Titles: {total_titles}")
        self.total_all_books_label.config(text=f"Total All Books: {total_books}")
