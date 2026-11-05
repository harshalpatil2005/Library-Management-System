import tkinter as tk
from tkinter import messagebox, ttk
from ui.login_window import LoginWindow
from ui.book_management import BookManagementWindow
from ui.member_management import MemberManagementWindow
from ui.activity_log_viewer import ActivityLogViewer
from ui.staff_management import StaffManagementWindow
from ui.reports_window import ReportsWindow
from ui.alerts_window import AlertsWindow  # <--- NEW IMPORT
from ui.issue_return import IssueReturnWindow

# --- UI Color Scheme (LIGHT GRAY THEME) ---
SIDEBAR_BG = "#EAEAEA"
SIDEBAR_FG = "#333333"
SIDEBAR_ACTIVE_BG = "#D4D4D4"
MAIN_CONTENT_BG = "#FFFFFF"
MAIN_CONTENT_FG = "#333333"
BUTTON_BG = "#5F7C9E"
BUTTON_FG = "#FFFFFF"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.withdraw()
        self.current_user = None

        self.login_window = LoginWindow(self)
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing_login)

    def on_closing_login(self):
        if self.current_user is None:
            if messagebox.askyesno("Exit", "Login cancelled. Do you want to exit the application?"):
                self.quit()
                self.destroy()

    def show_dashboard_layout(self, user):
        self.current_user = user
        self.deiconify()
        self.state('zoomed')
        self.title(f"Library Management System - Logged in as {user['Name']} ({user['Role']})")
        self.config(bg=MAIN_CONTENT_BG)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = tk.Frame(self, bg=SIDEBAR_BG, width=200)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.pack_propagate(False)

        self.create_sidebar_buttons(self.sidebar_frame)

        self.content_area_frame = tk.Frame(self, bg=MAIN_CONTENT_BG)
        self.content_area_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_area_frame.grid_columnconfigure(0, weight=1)
        self.content_area_frame.grid_rowconfigure(0, weight=1)

        self.show_dashboard_summary()

    def create_sidebar_buttons(self, parent_frame):
        button_font = ("Arial", 12, "bold")
        button_style = {"bg": SIDEBAR_BG, "fg": SIDEBAR_FG, "font": button_font,
                        "activebackground": SIDEBAR_ACTIVE_BG, "activeforeground": SIDEBAR_FG,
                        "relief": "flat", "pady": 10}

        tk.Label(parent_frame, text="Navigation", font=("Arial", 14, "bold"),
                 bg=SIDEBAR_BG, fg=SIDEBAR_FG, pady=20).pack(fill="x")

        ttk.Separator(parent_frame, orient="horizontal").pack(fill="x", pady=5, padx=5)

        tk.Button(parent_frame, text="Dashboard", command=self.show_dashboard_summary, **button_style).pack(fill="x",
                                                                                                            pady=5,
                                                                                                            padx=10)
        tk.Button(parent_frame, text="Member Management", command=self.show_member_management, **button_style).pack(
            fill="x", pady=5, padx=10)

        # Librarian-only features start here
        if self.current_user and self.current_user.get('Role') == 'Librarian':
            tk.Button(parent_frame, text="Staff Management", command=self.show_staff_management, **button_style).pack(
                fill="x", pady=5, padx=10)

        tk.Button(parent_frame, text="Book Management", command=self.show_book_management, **button_style).pack(
            fill="x", pady=5, padx=10)
        tk.Button(parent_frame, text="Issue/Return Books", command=self.show_issue_return, **button_style).pack(
            fill="x", pady=5, padx=10)

        # NEW Alerts & Overdue button, restricted to Librarian (for consistency)
        if self.current_user and self.current_user.get('Role') == 'Librarian':
            tk.Button(parent_frame, text="Alerts & Overdue", command=self.show_alerts, **button_style).pack(fill="x",
                                                                                                            pady=5,
                                                                                                            padx=10)
            tk.Button(parent_frame, text="Activity Log", command=self.show_activity_log, **button_style).pack(fill="x",
                                                                                                              pady=5,
                                                                                                              padx=10)
            tk.Button(parent_frame, text="Reports", command=self.show_reports, **button_style).pack(fill="x", pady=5,
                                                                                                    padx=10)

        ttk.Separator(parent_frame, orient="horizontal").pack(fill="x", pady=5, padx=5)

        logout_style = {"bg": BUTTON_BG, "fg": BUTTON_FG, "font": button_font,
                        "activebackground": "#4B627E", "activeforeground": BUTTON_FG,
                        "relief": "flat", "pady": 10}
        tk.Button(parent_frame, text="Logout", command=self.logout, **logout_style).pack(fill="x", pady=5, padx=10)

    def clear_content_area(self):
        for widget in self.content_area_frame.winfo_children():
            widget.destroy()

    def show_dashboard_summary(self):
        self.clear_content_area()
        user_name = self.current_user.get('Name', 'User') if self.current_user else 'Guest'
        user_role = self.current_user.get('Role', 'N/A') if self.current_user else 'N/A'

        # --- Greeting and Main Title ---
        tk.Label(self.content_area_frame, text="Library Dashboard", font=("Arial", 28, "bold"),
                 bg=MAIN_CONTENT_BG, fg=MAIN_CONTENT_FG).pack(pady=50)
        tk.Label(self.content_area_frame, text=f"Welcome, {user_name}! Your role is {user_role}.",
                 font=("Arial", 16), bg=MAIN_CONTENT_BG, fg=MAIN_CONTENT_FG).pack(pady=20)

        # --- Illogical, Aesthetic Quotes ---
        tk.Label(self.content_area_frame, text='"Reading gives us someplace to go when we have to stay where we are."',
                 font=("Arial", 18, "bold"),
                 bg=MAIN_CONTENT_BG, fg="#5F7C9E").pack(pady=(10, 5))
        tk.Label(self.content_area_frame, text="— Mason Cooley",
                 font=("Arial", 12),
                 bg=MAIN_CONTENT_BG, fg=MAIN_CONTENT_FG).pack(pady=(0, 20))
        tk.Label(self.content_area_frame, text='"A book is a device to ignite the imagination."',
                 font=("Arial", 20, "italic"),
                 bg=MAIN_CONTENT_BG, fg="#3498DB").pack(pady=(10, 5))
        tk.Label(self.content_area_frame, text="— Alan Bennett",
                 font=("Arial", 12),
                 bg=MAIN_CONTENT_BG, fg=MAIN_CONTENT_FG).pack(pady=(0, 40))

        # --- New Quote (Italicized) ---
        tk.Label(self.content_area_frame,
                 text="“The only thing that you absolutely have to know is the location of the library.”",
                 font=("Arial", 14, "italic"),
                 bg=MAIN_CONTENT_BG, fg=MAIN_CONTENT_FG).pack(pady=10)

        # --- Instruction Line (Now Italicized) ---
        tk.Label(self.content_area_frame, text="Use the navigation on the left to manage the library.",
                 font=("Arial", 14, "italic"), bg=MAIN_CONTENT_BG, fg=MAIN_CONTENT_FG).pack(pady=10)

    def show_member_management(self):
        self.clear_content_area()
        MemberManagementWindow(self.content_area_frame)

    def show_staff_management(self):
        if self.current_user.get('Role') == 'Librarian':
            self.clear_content_area()
            StaffManagementWindow(self.content_area_frame)
        else:
            messagebox.showerror("Permission Denied", "You do not have permission to access this feature.")

    def show_book_management(self):
        self.clear_content_area()
        BookManagementWindow(self.content_area_frame)

    def show_issue_return(self):
        self.clear_content_area()
        IssueReturnWindow(self.content_area_frame)

    def show_alerts(self):  # <--- NEW METHOD
        if self.current_user.get('Role') == 'Librarian':
            self.clear_content_area()
            AlertsWindow(self.content_area_frame).pack(fill="both", expand=True)
        else:
            messagebox.showerror("Permission Denied", "You do not have permission to access this feature.")

    def show_activity_log(self):
        if self.current_user.get('Role') == 'Librarian':
            self.clear_content_area()
            ActivityLogViewer(self.content_area_frame)
        else:
            messagebox.showerror("Permission Denied", "You do not have permission to access this feature.")

    def show_reports(self):
        if self.current_user.get('Role') == 'Librarian':
            self.clear_content_area()
            ReportsWindow(self.content_area_frame, role=self.current_user['Role']).pack(fill="both", expand=True)
        else:
            messagebox.showerror("Permission Denied", "You do not have permission to access this feature.")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.current_user = None
            self.withdraw()
            self.clear_content_area()

            if hasattr(self, 'login_window') and self.login_window:
                self.login_window.destroy()
            self.login_window = LoginWindow(self)
            self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing_login)

    def on_closing(self):
        if messagebox.askyesno("Exit", "Do you want to exit the application?"):
            self.quit()
            self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
