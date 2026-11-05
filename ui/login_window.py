import tkinter as tk
from tkinter import messagebox
from modules import auth

# --- System UI Colors ---
MAIN_BG = "#1F2C3A"      # Dark Main Background
FRAME_BG = "#16222A"     # Slightly lighter frame background
ACCENT_COLOR = "#00A388" # Teal Buttons / Highlights
TEXT_COLOR = "#FFFFFF"   # White Text
ENTRY_BG = "#2C3E50"     # Entry background
ENTRY_FG = "#FFFFFF"     # Entry text
ENTRY_FONT = ("Segoe UI", 13)
TITLE_FONT = ("Segoe UI", 20, "bold")
LABEL_FONT = ("Segoe UI", 12, "bold")
BUTTON_FONT = ("Segoe UI", 14, "bold")


class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Library Management System - Login")
        self.parent = parent
        self.configure(bg=MAIN_BG)
        self.geometry("500x400")
        self.resizable(False, False)
        self.create_widgets()
        self.center_window()

    def center_window(self):
        # Center the window on the screen
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')

    def create_widgets(self):
        # --- Frame for all widgets ---
        frame = tk.Frame(self, bg=FRAME_BG, padx=30, pady=30)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Title ---
        tk.Label(frame, text="Welcome to Library System", bg=FRAME_BG, fg=ACCENT_COLOR,
                 font=TITLE_FONT).pack(pady=(10, 25))

        # Username
        tk.Label(frame, text="USERNAME", bg=FRAME_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(anchor="w", pady=(5, 0))
        self.username_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=TEXT_COLOR)
        self.username_entry.pack(fill="x", pady=(0, 15))

        # Password
        tk.Label(frame, text="PASSWORD", bg=FRAME_BG, fg=TEXT_COLOR, font=LABEL_FONT).pack(anchor="w", pady=(5, 0))
        self.password_entry = tk.Entry(frame, show="*", font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=TEXT_COLOR)
        self.password_entry.pack(fill="x", pady=(0, 25))

        # Login Button
        self.login_button = tk.Button(frame, text="LOGIN", bg=ACCENT_COLOR, fg=TEXT_COLOR,
                                      font=BUTTON_FONT, relief="flat", command=self.handle_login)
        self.login_button.pack(fill="x", pady=(5, 10))

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = auth.login_user(username, password)

        if user:
            messagebox.showinfo("Login Success", f"Welcome, {user['Name']}!")
            self.destroy()
            self.parent.show_dashboard_layout(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
