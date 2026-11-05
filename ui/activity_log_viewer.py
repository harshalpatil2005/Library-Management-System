# ui/activity_log_viewer.py

import tkinter as tk
from tkinter import ttk
from modules import activity_log

# --- UI Color Scheme (must be defined or imported) ---
# Assuming these colors are consistent across your UI files
MAIN_CONTENT_BG = "#ECF0F1"


class ActivityLogViewer:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.create_widgets()
        self.load_logs()

    def create_widgets(self):
        # Create a main frame for this module's content inside the parent_frame
        self.main_content_frame = tk.Frame(self.parent_frame, bg=MAIN_CONTENT_BG)
        self.main_content_frame.pack(fill="both", expand=True)

        # Create a LabelFrame for better organization
        log_frame = tk.LabelFrame(self.main_content_frame, text="System Activity Log", bg=MAIN_CONTENT_BG, padx=10,
                                  pady=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Treeview to display logs
        columns = ("Log_ID", "User_Name", "Date_Time", "Action")
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show="headings")

        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150, anchor="center")

        # Use a grid layout for the Treeview and its scrollbar
        self.log_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure the grid to make the Treeview expand
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)

    def load_logs(self):
        """Loads all activity logs and displays them in the Treeview."""
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        logs = activity_log.get_all_logs()
        if logs:
            for log_item in logs:
                self.log_tree.insert("", "end", values=(
                    log_item['Log_ID'],
                    log_item['User_Name'],
                    log_item['Date_Time'],
                    log_item['Action']
                ))