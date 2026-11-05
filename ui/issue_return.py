import tkinter as tk
from tkinter import ttk, messagebox
from modules import issue_return, billing
from ui.bill_preview_window import BillPreviewWindow
import datetime

# --- UI Color Scheme (must be defined or imported) ---
MAIN_CONTENT_BG = "#ECF0F1"
BUTTON_BG = "#3498DB"
BUTTON_FG = "#FFFFFF"
FORM_LABEL_BG = MAIN_CONTENT_BG


class IssueReturnWindow:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        # Access current_user from the root window
        self.user_id = self.parent_frame.winfo_toplevel().current_user['User_ID']
        self.selected_member_id = None
        self.selected_book_id = None
        self.selected_issue_id = None
        self.fine_amount = 0.0

        # New variables for fine logic
        self.damaged_fine_var = tk.IntVar()
        self.damaged_fine_amount = 5.00  # Default fine for a damaged book

        self.create_widgets()

    def create_widgets(self):
        self.main_content_frame = tk.Frame(self.parent_frame, bg=MAIN_CONTENT_BG)
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=0)
        self.main_content_frame.grid_rowconfigure(1, weight=1)

        # --- Frame for Issue/Reserve a Book ---
        self.issue_frame = tk.LabelFrame(self.main_content_frame, text="Issue or Reserve a Book", bg=MAIN_CONTENT_BG,
                                         padx=15,
                                         pady=15)
        self.issue_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.issue_frame.columnconfigure(1, weight=1)

        tk.Label(self.issue_frame, text="Member ID:", bg=FORM_LABEL_BG).grid(row=0, column=0, sticky="w", pady=5)
        self.member_id_entry = tk.Entry(self.issue_frame)
        self.member_id_entry.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(self.issue_frame, text="Search Member", command=self.search_member, bg=BUTTON_BG, fg=BUTTON_FG,
                  relief="flat").grid(row=0, column=2, padx=5)
        self.member_info_label = tk.Label(self.issue_frame, text="", fg="blue", bg=FORM_LABEL_BG)
        self.member_info_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=5)

        tk.Label(self.issue_frame, text="Book ID:", bg=FORM_LABEL_BG).grid(row=2, column=0, sticky="w", pady=5)
        self.book_id_entry = tk.Entry(self.issue_frame)
        self.book_id_entry.grid(row=2, column=1, sticky="ew", padx=5)
        tk.Button(self.issue_frame, text="Search Book", command=self.search_book, bg=BUTTON_BG, fg=BUTTON_FG,
                  relief="flat").grid(row=2, column=2, padx=5)
        self.book_info_label = tk.Label(self.issue_frame, text="", fg="blue", bg=FORM_LABEL_BG)
        self.book_info_label.grid(row=3, column=0, columnspan=3, sticky="w", padx=5)

        # Buttons for Issue and Reserve Section
        issue_button_frame = tk.Frame(self.issue_frame, bg=MAIN_CONTENT_BG)
        issue_button_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")
        issue_button_frame.grid_columnconfigure(0, weight=1)
        issue_button_frame.grid_columnconfigure(1, weight=1)
        issue_button_frame.grid_columnconfigure(2, weight=1)

        self.issue_button = tk.Button(issue_button_frame, text="Issue Book", command=self.issue_book, state="disabled",
                                      bg=BUTTON_BG, fg=BUTTON_FG, relief="flat")
        self.issue_button.grid(row=0, column=0, padx=5, sticky="ew")

        # New "Reserve Book" button
        self.reserve_button = tk.Button(issue_button_frame, text="Reserve Book", command=self.reserve_book,
                                        state="disabled",
                                        bg=BUTTON_BG, fg=BUTTON_FG, relief="flat")
        self.reserve_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.print_issue_bill_button = tk.Button(issue_button_frame, text="Print Issue Bill",
                                                 command=self.print_issue_bill_button_action, state="disabled",
                                                 bg=BUTTON_BG, fg=BUTTON_FG, relief="flat")
        self.print_issue_bill_button.grid(row=0, column=2, padx=5, sticky="ew")

        # --- Frame for Return a Book ---
        self.return_frame = tk.LabelFrame(self.main_content_frame, text="Return a Book", bg=MAIN_CONTENT_BG, padx=15,
                                          pady=15)
        self.return_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.return_frame.columnconfigure(0, weight=1)
        self.return_frame.rowconfigure(0, weight=1)

        columns = ("Issue ID", "Title", "Issue Date", "Due Date")
        self.issued_books_tree = ttk.Treeview(self.return_frame, columns=columns, show="headings")
        for col in columns:
            self.issued_books_tree.heading(col, text=col)
            self.issued_books_tree.column(col, width=150, anchor="center")
        self.issued_books_tree.grid(row=0, column=0, columnspan=3, sticky="nsew", pady=10)
        self.issued_books_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        tree_scrollbar = ttk.Scrollbar(self.return_frame, orient="vertical", command=self.issued_books_tree.yview)
        tree_scrollbar.grid(row=0, column=3, sticky="ns", pady=10)
        self.issued_books_tree.configure(yscrollcommand=tree_scrollbar.set)

        billing_frame = tk.Frame(self.return_frame, bg=MAIN_CONTENT_BG)
        billing_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=10)

        self.fine_label = tk.Label(billing_frame, text="Overdue Fine: $0.00", fg="green", font=("Arial", 12, "bold"),
                                   bg=MAIN_CONTENT_BG)
        self.fine_label.pack(side="left", padx=10)

        # New: Checkbox for damaged book fine
        self.damaged_fine_checkbutton = tk.Checkbutton(billing_frame, text="Apply Damaged Book Fine",
                                                       variable=self.damaged_fine_var,
                                                       bg=MAIN_CONTENT_BG, font=("Arial", 10),
                                                       command=self.update_button_states)
        self.damaged_fine_checkbutton.pack(side="left", padx=10)

        self.return_button = tk.Button(billing_frame, text="Return Selected Book", command=self.return_book,
                                       state="disabled", bg=BUTTON_BG, fg=BUTTON_FG, relief="flat")
        self.return_button.pack(side="left", padx=10)

        self.pay_fine_button = tk.Button(billing_frame, text="Pay Fine", command=self.pay_fine, state="disabled",
                                         bg=BUTTON_BG, fg=BUTTON_FG, relief="flat")
        self.pay_fine_button.pack(side="left", padx=10)

        self.print_bill_button = tk.Button(billing_frame, text="Print Return Bill", command=self.print_bill_dialog,
                                           state="disabled", bg=BUTTON_BG, fg=BUTTON_FG, relief="flat")
        self.print_bill_button.pack(side="left", padx=10)

    def search_member(self):
        member_id = self.member_id_entry.get()
        if not member_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid Member ID.")
            return

        member_data = issue_return.get_member_by_id(int(member_id))
        if member_data:
            # Set the internal ID after successful search
            self.selected_member_id = member_data['User_ID']
            self.member_info_label.config(text=f"Member: {member_data['Name']} (ID: {member_data['User_ID']})")
            self.issue_button_state_check()
            self.load_issued_books(self.selected_member_id)
            self.update_button_states()
        else:
            # IMPORTANT: If search fails, it means DB_CONFIG is likely wrong in modules/issue_return.py
            self.selected_member_id = None
            self.member_info_label.config(
                text="Member not found. Check DB_CONFIG in modules/issue_return.py if this persists.")
            self.issue_button_state_check()
            self.clear_issued_books()
            self.update_button_states()

    def search_book(self):
        book_id = self.book_id_entry.get()
        if not book_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid Book ID.")
            return

        book_data = issue_return.get_book_by_id(int(book_id))  # Uses the function from modules/issue_return.py
        if book_data:
            # Set the internal ID after successful search
            self.selected_book_id = book_data['Book_ID']
            self.book_info_label.config(text=f"Book: {book_data['Title']} (Quantity: {book_data['Quantity']})")
            self.issue_button_state_check()
        else:
            self.selected_book_id = None
            self.book_info_label.config(text="Book not found.")
            self.issue_button_state_check()

    def issue_button_state_check(self):
        # Enable the buttons only if both IDs are set internally
        if self.selected_member_id and self.selected_book_id:
            self.issue_button.config(state="normal")
            self.print_issue_bill_button.config(state="normal")
            self.reserve_button.config(state="normal")
        else:
            self.issue_button.config(state="disabled")
            self.print_issue_bill_button.config(state="disabled")
            self.reserve_button.config(state="disabled")

    def issue_book(self):
        if self.selected_member_id and self.selected_book_id:
            success, message = issue_return.issue_book(self.user_id, self.selected_book_id, self.selected_member_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_issued_books(self.selected_member_id)
                self.search_book()
                self.selected_issue_id = None
                self.update_button_states()

                # --- AUTOMATIC ISSUE BILL GENERATION ---
                self.print_issue_bill_button_action()
                # ---------------------------------------
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showerror("Error", "Please select a member and a book first.")

    # Method to handle the reserve button
    def reserve_book(self):
        if self.selected_member_id and self.selected_book_id:
            success, message = issue_return.reserve_book(self.selected_book_id, self.selected_member_id)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showerror("Error", "Please select a member and a book first.")

    def print_issue_bill_button_action(self):
        member_id = self.selected_member_id
        book_id = self.selected_book_id

        if member_id and book_id:
            try:
                # Need to fetch the book title for the bill content (using the backend module)
                book_data = issue_return.get_book_by_id(book_id)
                book_title = book_data['Title'] if book_data else f"Book ID: {book_id} (Title Not Found)"

                bill_content, default_filename = self.generate_issue_bill_content(member_id, book_id, book_title)
                BillPreviewWindow(self.parent_frame.winfo_toplevel(), bill_content, default_filename)
            except Exception as e:
                # Catch any remaining exception and show a user-friendly error
                messagebox.showerror("Error", f"Could not generate issue bill: {e}")
        else:
            messagebox.showerror("Error", "Please search and select a valid member and book first.")

    # ---------------------------------------------------------------------------------------

    def load_issued_books(self, member_id):
        for item in self.issued_books_tree.get_children():
            self.issued_books_tree.delete(item)

        books_list = issue_return.get_issued_books_by_member(member_id)
        if books_list:
            for book_item in books_list:
                self.issued_books_tree.insert("", "end", values=(
                    book_item['Issue_ID'],
                    book_item['Title'],
                    book_item['Issue_Date'],
                    book_item['Due_Date']
                ))
        self.update_button_states()

    def clear_issued_books(self):
        for item in self.issued_books_tree.get_children():
            self.issued_books_tree.delete(item)
        self.selected_issue_id = None
        self.fine_amount = 0.0
        self.update_button_states()

    def on_tree_select(self, event=None):
        selected_item = self.issued_books_tree.focus()
        if selected_item:
            self.selected_issue_id = self.issued_books_tree.item(selected_item, 'values')[0]

            # --- IMPORTANT: Get the correct member ID from the entry field for fine calculation
            member_id = self.member_id_entry.get()
            if member_id and member_id.isdigit():
                fine_amount, _ = billing.calculate_fine(self.selected_issue_id)
                self.fine_amount = fine_amount
            else:
                self.fine_amount = 0.0
        else:
            self.selected_issue_id = None
            self.fine_amount = 0.0

        self.update_button_states()

    def update_button_states(self):
        if self.selected_issue_id:
            self.return_button.config(state="normal")
            self.print_bill_button.config(state="normal")
            self.damaged_fine_checkbutton.config(state="normal")

            # Corrected logic to calculate the total fine
            is_damaged = bool(self.damaged_fine_var.get())
            total_fine = self.fine_amount + (self.damaged_fine_amount if is_damaged else 0)

            if total_fine > 0:
                self.fine_label.config(text=f"Total Fine: ${total_fine:.2f}", fg="red")
                self.pay_fine_button.config(state="normal")
            else:
                self.fine_label.config(text="Total Fine: $0.00", fg="green")
                self.pay_fine_button.config(state="disabled")
        else:
            self.return_button.config(state="disabled")
            self.pay_fine_button.config(state="disabled")
            self.print_bill_button.config(state="disabled")
            self.fine_label.config(text="Fine: $0.00", fg="black")
            self.damaged_fine_checkbutton.config(state="disabled")
            self.damaged_fine_var.set(0)

    def return_book(self):
        selected_item = self.issued_books_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an issued book to return.")
            return

        issue_id = self.issued_books_tree.item(selected_item, 'values')[0]

        is_damaged = bool(self.damaged_fine_var.get())
        overdue_fine, _ = billing.calculate_fine(issue_id)

        total_fine = overdue_fine + (self.damaged_fine_amount if is_damaged else 0)

        if total_fine > 0:
            # We skip the fine prompt here to allow automatic bill generation after return
            # The fine is recorded but payment is tracked separately (or assumed paid).
            pass

        # Pass the damaged status to the backend function
        success, message = issue_return.return_book(self.user_id, issue_id, is_damaged)

        if success:
            messagebox.showinfo("Success", message)
            self.load_issued_books(self.selected_member_id)
            self.search_book()

            # --- AUTOMATIC RETURN BILL GENERATION ---
            bill_content, default_filename = self.generate_return_bill_content(issue_id, overdue_fine, is_damaged)
            BillPreviewWindow(self.parent_frame.winfo_toplevel(), bill_content, default_filename)
            # ----------------------------------------
        else:
            messagebox.showerror("Error", message)

    def pay_fine(self):
        # ... (Existing fine payment logic remains the same, shows bill preview) ...
        if not self.selected_issue_id:
            messagebox.showerror("Error", "Please select an issued book to process the fine.")
            return

        # 2. Calculate fine details
        overdue_fine, _ = billing.calculate_fine(self.selected_issue_id)
        is_damaged = bool(self.damaged_fine_var.get())
        total_fine = overdue_fine + (self.damaged_fine_amount if is_damaged else 0)

        if total_fine <= 0:
            messagebox.showinfo("No Fine", "There is no fine to pay.")
            return

        # SIMPLIFIED LOGIC FOR PROJECT DEMO
        try:
            # 3. Generate the bill content using the return bill generator
            bill_content, default_filename = self.generate_return_bill_content(
                self.selected_issue_id, overdue_fine, is_damaged
            )

            # 4. Show the bill preview window
            BillPreviewWindow(self.parent_frame.winfo_toplevel(), bill_content, default_filename)

            messagebox.showinfo("Bill Generated",
                                "Bill generated successfully for fine payment (Database update skipped).")

        except Exception as e:
            messagebox.showerror("Error Generating Bill", f"An error occurred while generating the bill: {e}")

        # 5. Refresh the state, as if payment was completed
        self.load_issued_books(self.selected_member_id)
        self.on_tree_select()

    def print_bill_dialog(self):
        if not self.selected_issue_id:
            messagebox.showerror("Error", "Please select an issue record to view a bill.")
            return

        overdue_fine, _ = billing.calculate_fine(self.selected_issue_id)

        # Check if the book has already been returned
        db = issue_return.DatabaseManager()
        db.connect()
        query = "SELECT Book_ID FROM Issue_Record WHERE Issue_ID = %s"
        record = db.fetch_one(query, (self.selected_issue_id,))
        db.close()

        if record:
            book_id = record['Book_ID']
            # Now check if it's returned
            is_returned_query = "SELECT Return_Date FROM Issue_Record WHERE Issue_ID = %s"
            db.connect()
            return_record = db.fetch_one(is_returned_query, (self.selected_issue_id,))
            db.close()

            if return_record and return_record['Return_Date']:
                # It's a return bill
                is_damaged = bool(self.damaged_fine_var.get())
                bill_content, default_filename = self.generate_return_bill_content(self.selected_issue_id, overdue_fine,
                                                                                   is_damaged)
                BillPreviewWindow(self.parent_frame.winfo_toplevel(), bill_content, default_filename)
            else:
                # It's an issue bill
                book_data = issue_return.get_book_by_id(book_id)
                book_title = book_data['Title'] if book_data else f"Book ID: {book_id} (Title Not Found)"
                bill_content, default_filename = self.generate_issue_bill_content(self.selected_member_id, book_id,
                                                                                  book_title)
                BillPreviewWindow(self.parent_frame.winfo_toplevel(), bill_content, default_filename)
        else:
            messagebox.showerror("Error", "Issue record not found.")

    def generate_issue_bill_content(self, member_id, book_id, book_title):
        member_info = issue_return.get_member_by_id(member_id)

        if not member_info:
            return "Error: Could not retrieve info for bill.", "error.txt"

        issue_date = datetime.date.today()
        due_date = issue_date + datetime.timedelta(days=14)

        bill_content = f"""
        -------------------------------------------
            LIBRARY BOOK ISSUE RECEIPT
        -------------------------------------------
        Transaction Date: {issue_date}
        Staff ID: {self.user_id}

        Member Name: {member_info['Name']}
        Member ID: {member_info['User_ID']}

        Book Title: {book_title}
        Book ID: {book_id}

        Issue Date: {issue_date}
        Due Date: {due_date}

        -------------------------------------------
        Please return the book on or before the due date to avoid fines.
        """
        return bill_content, f"issue_receipt_{member_id}_{book_id}.txt"

    def generate_return_bill_content(self, issue_id, overdue_fine, is_damaged):
        db = issue_return.DatabaseManager()
        db.connect()
        query = """
        SELECT ir.Issue_ID, b.Title, b.Book_ID, ir.Issue_Date, ir.Due_Date, ir.User_ID
        FROM Issue_Record ir
        JOIN Book b ON ir.Book_ID = b.Book_ID
        WHERE ir.Issue_ID = %s
        """
        issue_info = db.fetch_one(query, (issue_id,))
        db.close()

        if not issue_info:
            return "Error: Could not retrieve issue record for bill.", "error.txt"

        member_info = issue_return.get_member_by_id(issue_info['User_ID'])
        if not member_info:
            return "Error: Could not retrieve member info for bill.", "error.txt"

        damaged_fine = self.damaged_fine_amount if is_damaged else 0.0
        total_fine = overdue_fine + damaged_fine

        fine_details = f"Overdue Fine: ${overdue_fine:.2f}\n"
        if is_damaged:
            fine_details += f"Damaged Book Fine: ${damaged_fine:.2f}\n"
        fine_details += f"Total Fine: ${total_fine:.2f}"

        # Ensure dates are strings for display
        issue_date_str = issue_info['Issue_Date'].strftime('%Y-%m-%d') if isinstance(issue_info['Issue_Date'],
                                                                                     datetime.date) else str(
            issue_info['Issue_Date'])
        due_date_str = issue_info['Due_Date'].strftime('%Y-%m-%d') if isinstance(issue_info['Due_Date'],
                                                                                 datetime.date) else str(
            issue_info['Due_Date'])

        bill_content = f"""
        -------------------------------------------
            LIBRARY BOOK RETURN RECEIPT
        -------------------------------------------
        Transaction Date: {datetime.date.today()}
        Staff ID: {self.user_id}

        Member Name: {member_info['Name']}
        Member ID: {member_info['User_ID']}

        Book Title: {issue_info['Title']}
        Issue ID: {issue_id}

        Issue Date: {issue_date_str}
        Due Date: {due_date_str}
        Return Date: {datetime.date.today()}

        {fine_details}
        Payment Status: {"Paid" if total_fine > 0 else "N/A"}

        -------------------------------------------
        Thank you for your timely return.
        """
        return bill_content, f"return_receipt_{issue_id}.txt"
