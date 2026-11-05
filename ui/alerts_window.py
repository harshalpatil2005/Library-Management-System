import tkinter as tk
from tkinter import ttk, messagebox
from modules import overdue_alerts
import datetime

# --- UI Color Scheme (placeholders, assume they are defined elsewhere) ---
MAIN_CONTENT_BG = "#ECF0F1"
FORM_LABEL_BG = MAIN_CONTENT_BG


class AlertsWindow:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.create_widgets()
        # Load the data immediately upon initialization
        self.load_alerts()

    def create_widgets(self):
        self.main_content_frame = tk.Frame(self.parent_frame, bg=MAIN_CONTENT_BG)
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=0)
        self.main_content_frame.grid_rowconfigure(1, weight=1)
        self.main_content_frame.grid_rowconfigure(2, weight=1)

        # --- Header and Refresh ---
        header_frame = tk.Frame(self.main_content_frame, bg=MAIN_CONTENT_BG)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.columnconfigure(0, weight=1)

        self.overdue_count_label = tk.Label(
            header_frame,
            text="Loading Alerts...",
            font=("Arial", 14, "bold"),
            bg=FORM_LABEL_BG,
            fg="#E74C3C"
        )
        self.overdue_count_label.grid(row=0, column=0, sticky="w")

        ttk.Button(header_frame, text="Refresh Alerts", command=self.load_alerts).grid(row=0, column=1, sticky="e", padx=10)

        # --- Overdue Books Frame ---
        self.overdue_frame = tk.LabelFrame(
            self.main_content_frame,
            text="Overdue Books (High Priority)",
            bg=MAIN_CONTENT_BG,
            padx=10,
            pady=10,
            fg="#C0392B"
        )
        self.overdue_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        self.overdue_frame.columnconfigure(0, weight=1)
        self.overdue_frame.rowconfigure(0, weight=1)

        overdue_cols = ("Issue ID", "Book Title", "Member Name", "Due Date", "Days Overdue", "Fine Due ($)")
        self.overdue_tree = ttk.Treeview(self.overdue_frame, columns=overdue_cols, show="headings")

        # Configure columns
        self.overdue_tree.heading("Issue ID", text="Issue ID")
        self.overdue_tree.column("Issue ID", width=60, anchor="center")
        self.overdue_tree.heading("Book Title", text="Book Title")
        self.overdue_tree.column("Book Title", width=200, anchor="w")
        self.overdue_tree.heading("Member Name", text="Member Name")
        self.overdue_tree.column("Member Name", width=150, anchor="w")
        self.overdue_tree.heading("Due Date", text="Due Date")
        self.overdue_tree.column("Due Date", width=100, anchor="center")
        self.overdue_tree.heading("Days Overdue", text="Days Overdue")
        self.overdue_tree.column("Days Overdue", width=80, anchor="center")
        self.overdue_tree.heading("Fine Due ($)", text="Fine Due ($)")
        self.overdue_tree.column("Fine Due ($)", width=100, anchor="center")

        self.overdue_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for Overdue Books
        overdue_scrollbar = ttk.Scrollbar(self.overdue_frame, orient="vertical", command=self.overdue_tree.yview)
        overdue_scrollbar.grid(row=0, column=1, sticky="ns")
        self.overdue_tree.configure(yscrollcommand=overdue_scrollbar.set)

        # --- Ready Reservations Frame ---
        self.reservations_frame = tk.LabelFrame(
            self.main_content_frame,
            text="Reservations Ready for Pickup",
            bg=MAIN_CONTENT_BG,
            padx=10,
            pady=10,
            fg="#27AE60"
        )
        self.reservations_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        self.reservations_frame.columnconfigure(0, weight=1)
        self.reservations_frame.rowconfigure(0, weight=1)

        res_cols = ("Reservation ID", "Book Title", "Member Name", "Reservation Date")
        self.reservations_tree = ttk.Treeview(self.reservations_frame, columns=res_cols, show="headings")

        # Configure columns
        self.reservations_tree.heading("Reservation ID", text="Res ID")
        self.reservations_tree.column("Reservation ID", width=60, anchor="center")
        self.reservations_tree.heading("Book Title", text="Book Title")
        self.reservations_tree.column("Book Title", width=200, anchor="w")
        self.reservations_tree.heading("Member Name", text="Member Name")
        self.reservations_tree.column("Member Name", width=150, anchor="w")
        self.reservations_tree.heading("Reservation Date", text="Reserved On")
        self.reservations_tree.column("Reservation Date", width=100, anchor="center")

        self.reservations_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for Ready Reservations
        res_scrollbar = ttk.Scrollbar(self.reservations_frame, orient="vertical", command=self.reservations_tree.yview)
        res_scrollbar.grid(row=0, column=1, sticky="ns")
        self.reservations_tree.configure(yscrollcommand=res_scrollbar.set)

    def load_alerts(self):
        # Clear existing data
        for item in self.overdue_tree.get_children():
            self.overdue_tree.delete(item)
        for item in self.reservations_tree.get_children():
            self.reservations_tree.delete(item)

        try:
            # 1. Load Overdue Count
            overdue_count = overdue_alerts.get_overdue_count()
            if overdue_count > 0:
                self.overdue_count_label.config(text=f"Total Overdue Books: {overdue_count}", fg="#E74C3C")
            else:
                self.overdue_count_label.config(text="No Overdue Books! System Clear.", fg="#27AE60")

            # 2. Load Overdue Books Details
            overdue_list = overdue_alerts.get_all_overdue_books()
            for book in overdue_list:
                fine_amount = f"{book['Overdue_Fine']:.2f}"
                self.overdue_tree.insert("", "end", values=(
                    book['Issue_ID'],
                    book['Title'],
                    book['Member_Name'],   # fixed here
                    book['Due_Date'],
                    book['Overdue_Days'],
                    fine_amount
                ))

            # 3. Load Ready Reservations
            ready_reservations = overdue_alerts.get_ready_reservations()
            for res in ready_reservations:
                self.reservations_tree.insert("", "end", values=(
                    res['Reservation_ID'],
                    res['Title'],
                    res['Member_Name'],   # fixed here
                    res['Reservation_Date']
                ))

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load alerts data: {e}")
            self.overdue_count_label.config(text="Alerts Failed to Load.", fg="#C0392B")
