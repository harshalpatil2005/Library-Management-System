# ui/member_management.py

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


class MemberManagementWindow:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        # Safely access admin_id
        try:
            self.admin_id = self.parent_frame.winfo_toplevel().current_user['User_ID']
        except AttributeError:
            self.admin_id = "ADMIN_ID_UNKNOWN"
            messagebox.showwarning("User Context", "Could not retrieve Admin ID. Using placeholder.")

        self.create_widgets()
        self.load_members()

    def create_widgets(self):
        self.main_content_frame = tk.Frame(self.parent_frame, bg=MAIN_CONTENT_BG)
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(1, weight=3)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        self.form_frame = tk.LabelFrame(self.main_content_frame, text="Manage Members", bg=MAIN_CONTENT_BG, padx=15,
                                        pady=15)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

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
        # Note: Password is only required for ADD. For UPDATE, it's optional but validated if present.
        self.entry_password = tk.Entry(self.form_frame, show="*")
        self.entry_password.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        # The role for this module is always "Member"
        tk.Label(self.form_frame, text="Role:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.role_var = tk.StringVar(self.form_frame, value="Member")
        self.role_label = tk.Label(self.form_frame, textvariable=self.role_var, bg=FORM_LABEL_BG)
        self.role_label.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Contact:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_contact = tk.Entry(self.form_frame)
        self.entry_contact.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="Email:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.entry_email = tk.Entry(self.form_frame)
        self.entry_email.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        row_num += 1

        tk.Label(self.form_frame, text="User Type:", bg=FORM_LABEL_BG).grid(row=row_num, column=0, sticky="w", pady=5)
        self.user_type_var = tk.StringVar(self.form_frame)
        # Member types based on user requirements: student, faculty, staff, other
        self.user_type_combobox = ttk.Combobox(self.form_frame, textvariable=self.user_type_var,
                                               values=["Student", "Faculty", "Staff", "Other"], state="readonly")
        self.user_type_combobox.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")
        self.user_type_combobox.current(0)
        row_num += 1

        self.form_frame.grid_columnconfigure(1, weight=1)

        button_style = {"bg": BUTTON_BG, "fg": BUTTON_FG, "font": ("Arial", 10, "bold"), "relief": "flat"}

        button_frame = tk.Frame(self.form_frame, bg=MAIN_CONTENT_BG)
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Updated button commands to use validated methods
        self.button_add = tk.Button(button_frame, text="Add Member", command=self.add_member_validated, **button_style)
        self.button_add.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        self.button_update = tk.Button(button_frame, text="Update Member", command=self.update_member_validated,
                                       **button_style)
        self.button_update.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        self.button_delete = tk.Button(button_frame, text="Delete Member", command=self.delete_member_validated,
                                       **button_style)
        self.button_delete.grid(row=1, column=0, pady=5, padx=5, sticky="ew")

        self.button_clear = tk.Button(button_frame, text="Clear Form", command=self.clear_form, **button_style)
        self.button_clear.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        self.members_tree_frame = tk.LabelFrame(self.main_content_frame, text="Member List", bg=MAIN_CONTENT_BG,
                                                padx=10, pady=10)
        self.members_tree_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.members_tree_frame.grid_columnconfigure(0, weight=1)
        self.members_tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("User_ID", "Name", "Username", "Role", "Contact", "Email", "User_Type")
        self.members_tree = ttk.Treeview(self.members_tree_frame, columns=columns, show="headings")

        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=100, anchor="center")

        self.members_tree.grid(row=0, column=0, sticky="nsew")
        self.members_tree.bind("<ButtonRelease-1>", self.select_member)

        scrollbar = ttk.Scrollbar(self.members_tree_frame, orient="vertical", command=self.members_tree.yview)
        self.members_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    # --- NEW VALIDATION METHOD ---
    def validate_member_input(self, is_update=False):
        """
        Validates all input fields based on type requirements.
        If is_update is True, password is not strictly required.
        """
        data = {
            'name': self.entry_name.get().strip(),
            'username': self.entry_username.get().strip(),
            'password': self.entry_password.get(),
            'role': self.role_var.get(),
            'contact': self.entry_contact.get().strip(),
            'email': self.entry_email.get().strip(),
            'user_type': self.user_type_combobox.get()
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
            errors.append("Password is required for adding a new member.")
        elif data['password'] and len(data['password']) < 6:
            errors.append("Password must be at least 6 characters long.")

        # 4. Contact: Required, must be numeric, min 8 digits
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

        # 6. User Type: Required (Combobox selection)
        if not data['user_type']:
            errors.append("User Type must be selected.")

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return None

        return data

    # --- MODIFIED CRUD METHODS TO USE VALIDATION ---
    def add_member_validated(self):
        """Adds a new member after validating the form data."""
        # is_update=False by default for ADD operation
        validated_data = self.validate_member_input(is_update=False)
        if validated_data is None:
            return

        name = validated_data['name']
        username = validated_data['username']
        password = validated_data['password']  # Password is required for ADD
        role = validated_data['role']
        contact = validated_data['contact']
        email = validated_data['email']
        user_type = validated_data['user_type']

        if member.add_member(self.admin_id, name, username, password, role, contact, email, user_type):
            messagebox.showinfo("Success", "Member added successfully!")
            self.clear_form()
            self.load_members()
        else:
            messagebox.showerror("Error", "Failed to add member. Username may already exist or database error.")

    def update_member_validated(self):
        """Updates the selected member after validating the form data."""
        selected_item = self.members_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a member to update.")
            return

        member_id = self.members_tree.item(selected_item, 'values')[0]

        # is_update=True allows an empty password field if no change is intended
        validated_data = self.validate_member_input(is_update=True)
        if validated_data is None:
            return

        name = validated_data['name']
        username = validated_data['username']
        password = validated_data['password']  # This can be empty, update_member handles it
        role = validated_data['role']
        contact = validated_data['contact']
        email = validated_data['email']
        user_type = validated_data['user_type']

        if member.update_member(self.admin_id, member_id, name, username, password, role, contact, email, user_type):
            messagebox.showinfo("Success", "Member updated successfully!")
            self.clear_form()
            self.load_members()
        else:
            messagebox.showerror("Error", "Failed to update member.")

    def delete_member_validated(self):
        """Deletes the selected member (validation is only for selection)."""
        selected_item = self.members_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a member to delete.")
            return

        member_id = self.members_tree.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user ID {member_id}?"):
            if member.delete_member(self.admin_id, member_id):
                messagebox.showinfo("Success", "Member deleted successfully.")
                self.clear_form()
                self.load_members()
            else:
                messagebox.showerror("Error", "Failed to delete member.")

    # --- Remaining methods unchanged (or slightly adjusted for consistency) ---

    def load_members(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)

        members_list = member.get_all_members()
        if members_list:
            for member_item in members_list:
                self.members_tree.insert("", "end", values=(
                    member_item['User_ID'],
                    member_item['Name'],
                    member_item['Username'],
                    member_item['Role'],
                    member_item['Contact'],
                    member_item['Email'],
                    member_item['User_Type']
                ))

    def select_member(self, event):
        selected_item = self.members_tree.focus()
        if selected_item:
            member_data = self.members_tree.item(selected_item, 'values')
            self.clear_form()
            self.entry_name.insert(0, member_data[1])
            self.entry_username.insert(0, member_data[2])
            # Do NOT populate password for security reasons
            self.entry_contact.insert(0, member_data[4])
            self.entry_email.insert(0, member_data[5])
            self.user_type_combobox.set(member_data[6])

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_contact.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        # Reset user type to the first option
        self.user_type_combobox.current(0)
