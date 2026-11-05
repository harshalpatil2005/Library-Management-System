import tkinter as tk
from tkinter import ttk, messagebox
from modules import member
import re  # Import for regular expression validation

# --- UI Color Scheme (must be defined or imported) ---
MAIN_CONTENT_BG = "#ECF0F1"
BUTTON_BG = "#3498DB"
BUTTON_FG = "#FFFFFF"
FORM_LABEL_BG = MAIN_CONTENT_BG
ERROR_FG = "#CC3333"  # Define a color for error visibility


class StaffManagementWindow:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        # Safely access admin_id
        try:
            self.admin_id = self.parent_frame.winfo_toplevel().current_user['User_ID']
        except AttributeError:
            self.admin_id = "ADMIN_ID_UNKNOWN"
            messagebox.showwarning("User Context", "Could not retrieve Admin ID. Using placeholder.")

        self.create_widgets()
        self.load_staff()

    def create_widgets(self):
        self.main_content_frame = tk.Frame(self.parent_frame, bg=MAIN_CONTENT_BG)
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(1, weight=3)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # Frame for the form
        self.form_frame = tk.LabelFrame(self.main_content_frame, text="Manage Staff", bg=MAIN_CONTENT_BG, padx=15,
                                        pady=15)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Labels and Entry fields
        row_num = 0
        tk.Label(self.form_frame, text="Name:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_name = tk.Entry(self.form_frame)
        self.entry_name.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Username:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_username = tk.Entry(self.form_frame)
        self.entry_username.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Password:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_password = tk.Entry(self.form_frame, show="*")
        self.entry_password.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Role:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.role_var = tk.StringVar(self.form_frame)
        # Staff can only be Librarians or other staff roles
        self.role_combobox = ttk.Combobox(self.form_frame, textvariable=self.role_var, values=["Librarian", "Staff"],
                                          state="readonly")
        self.role_combobox.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        self.role_combobox.current(0)  # Default to Librarian
        row_num += 1

        tk.Label(self.form_frame, text="Contact:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_contact = tk.Entry(self.form_frame)
        self.entry_contact.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Email:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_email = tk.Entry(self.form_frame)
        self.entry_email.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        self.form_frame.grid_columnconfigure(1, weight=1)

        # Buttons for actions
        button_style = {"bg": BUTTON_BG, "fg": BUTTON_FG, "font": ("Arial", 10, "bold"), "relief": "flat"}

        button_frame = tk.Frame(self.form_frame, bg=MAIN_CONTENT_BG)
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Updated button commands to use validated methods
        self.button_add = tk.Button(button_frame, text="Add Staff", command=self.add_staff_validated, **button_style)
        self.button_add.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        self.button_update = tk.Button(button_frame, text="Update Staff", command=self.update_staff_validated,
                                       **button_style)
        self.button_update.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        self.button_delete = tk.Button(button_frame, text="Delete Staff", command=self.delete_staff_validated,
                                       **button_style)
        self.button_delete.grid(row=1, column=0, pady=5, padx=5, sticky="ew")

        self.button_clear = tk.Button(button_frame, text="Clear Form", command=self.clear_form, **button_style)
        self.button_clear.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        # Treeview to display members
        self.staff_tree_frame = tk.LabelFrame(self.main_content_frame, text="Staff List", bg=MAIN_CONTENT_BG, padx=10,
                                              pady=10)
        self.staff_tree_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.staff_tree_frame.grid_columnconfigure(0, weight=1)
        self.staff_tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("User_ID", "Name", "Username", "Role", "Contact", "Email")
        self.staff_tree = ttk.Treeview(self.staff_tree_frame, columns=columns, show="headings")

        for col in columns:
            self.staff_tree.heading(col, text=col)
            self.staff_tree.column(col, width=100, anchor="center")

        self.staff_tree.grid(row=0, column=0, sticky="nsew")
        self.staff_tree.bind("<ButtonRelease-1>", self.select_staff)

        scrollbar = ttk.Scrollbar(self.staff_tree_frame, orient="vertical", command=self.staff_tree.yview)
        self.staff_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    # --- NEW VALIDATION METHOD ---
    def validate_staff_input(self, is_update=False):
        """
        Validates all input fields based on type requirements for staff management.
        If is_update is True, password is not strictly required.
        """
        data = {
            'name': self.entry_name.get().strip(),
            'username': self.entry_username.get().strip(),
            'password': self.entry_password.get(),
            'role': self.role_var.get(),
            'contact': self.entry_contact.get().strip(),
            'email': self.entry_email.get().strip(),
        }

        errors = []

        # 1. Name: Required, letters and spaces only
        name_regex = r"^[a-zA-Z\s]+$"
        if not data['name']:
            errors.append("Name is required.")
        elif not re.match(name_regex, data['name']):
            errors.append("Name must contain only letters and spaces.")

        # 2. Username: Required, alphanumeric (and underscore allowed) only, min 3 chars
        username_regex = r"^[a-zA-Z0-9_]+$"
        if not data['username']:
            errors.append("Username is required.")
        elif not re.match(username_regex, data['username']):
            errors.append("Username must be alphanumeric (letters, numbers, or underscore).")
        elif len(data['username']) < 3:
            errors.append("Username must be at least 3 characters long.")

        # 3. Password: Required for ADD, optional but validated if provided for UPDATE (min 6 chars)
        if not data['password'] and not is_update:
            errors.append("Password is required for adding new staff.")
        elif data['password'] and len(data['password']) < 6:
            errors.append("Password must be at least 6 characters long.")

        # 4. Contact: Required, must be numeric, 8-15 digits
        contact_regex = r"^\d{8,15}$"  # Allows 8 to 15 digits
        if not data['contact']:
            errors.append("Contact number is required.")
        elif not re.match(contact_regex, data['contact']):
            errors.append("Contact number must be 8-15 digits long and numeric only.")

        # 5. Email: Required, must match basic email format
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not data['email']:
            errors.append("Email is required.")
        elif not re.match(email_regex, data['email']):
            errors.append("Email format is invalid (e.g., user@domain.com).")

        # 6. Role: Ensure role is one of the allowed types (redundant due to combobox, but good practice)
        if data['role'] not in ["Librarian", "Staff"]:
            errors.append("Role must be 'Librarian' or 'Staff'.")

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return None

        return data

    # --- MODIFIED CRUD METHODS TO USE VALIDATION ---
    def add_staff_validated(self):
        """Adds a new staff member after validating the form data."""
        validated_data = self.validate_staff_input(is_update=False)
        if validated_data is None:
            return

        if member.add_staff(self.admin_id, **validated_data):
            messagebox.showinfo("Success", "Staff member added successfully!")
            self.clear_form()
            self.load_staff()
        else:
            messagebox.showerror("Error", "Failed to add staff member. Username may already exist or database error.")

    def update_staff_validated(self):
        """Updates the selected staff member after validating the form data."""
        selected_item = self.staff_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a staff member to update.")
            return

        staff_id = self.staff_tree.item(selected_item, 'values')[0]

        validated_data = self.validate_staff_input(is_update=True)
        if validated_data is None:
            return

        # member.update_staff expects: (admin_id, staff_id, name, username, password, role, contact, email)
        args = (
            self.admin_id,
            staff_id,
            validated_data['name'],
            validated_data['username'],
            validated_data['password'],
            validated_data['role'],
            validated_data['contact'],
            validated_data['email']
        )

        if member.update_staff(*args):
            messagebox.showinfo("Success", "Staff member updated successfully!")
            self.clear_form()
            self.load_staff()
        else:
            messagebox.showerror("Error", "Failed to update staff member.")

    def delete_staff_validated(self):
        """Deletes the selected staff member."""
        selected_item = self.staff_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a staff member to delete.")
            return

        staff_id = self.staff_tree.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete staff member ID {staff_id}?"):
            if member.delete_staff(self.admin_id, staff_id):
                messagebox.showinfo("Success", "Staff member deleted successfully.")
                self.clear_form()
                self.load_staff()
            else:
                messagebox.showerror("Error", "Failed to delete staff member.")

    def load_staff(self):
        """Loads all staff members from the database and displays them in the Treeview."""
        for item in self.staff_tree.get_children():
            self.staff_tree.delete(item)

        staff_members = member.get_all_staff()
        if staff_members:
            for staff_item in staff_members:
                self.staff_tree.insert("", "end", values=(
                    staff_item['User_ID'],
                    staff_item['Name'],
                    staff_item['Username'],
                    staff_item['Role'],
                    staff_item['Contact'],
                    staff_item['Email']
                ))

    def select_staff(self, event):
        """Populates the form with data from the selected row."""
        selected_item = self.staff_tree.focus()
        if selected_item:
            staff_data = self.staff_tree.item(selected_item, 'values')
            self.clear_form()
            self.entry_name.insert(0, staff_data[1])
            self.entry_username.insert(0, staff_data[2])
            self.role_combobox.set(staff_data[3])
            self.entry_contact.insert(0, staff_data[4])
            self.entry_email.insert(0, staff_data[5])
            # The password field is intentionally left blank for security

    def clear_form(self):
        """Clears all entry fields in the form."""
        self.entry_name.delete(0, tk.END)
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.role_combobox.set("Librarian")
        self.entry_contact.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
