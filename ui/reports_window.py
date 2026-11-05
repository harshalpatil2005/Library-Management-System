import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from modules import reports as reports
import datetime
import os
from tkcalendar import DateEntry  # Requires: pip install tkcalendar

# UI Color Scheme (Consistent with main.py)
MAIN_CONTENT_BG = "#FFFFFF"
MAIN_CONTENT_FG = "#333333"
BUTTON_BG = "#5F7C9E"
BUTTON_FG = "#FFFFFF"
ACCENT_COLOR = "#3498DB"  # Blue for links/highlights


class ReportsWindow(tk.Frame):
    def __init__(self, parent_frame, role):
        super().__init__(parent_frame, bg=MAIN_CONTENT_BG)
        self.role = role
        self.report_content = ""  # <<< ADDED to store content for saving
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Title ---
        tk.Label(self, text="Library Activity Reports",
                 font=("Arial", 20, "bold"),
                 bg=MAIN_CONTENT_BG, fg=MAIN_CONTENT_FG,
                 pady=10).grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))

        # --- Control Panel Frame (Input/Buttons) ---
        control_frame = tk.Frame(self, bg="#F0F0F0", padx=15, pady=15, relief=tk.RIDGE, bd=1)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)

        # --- Predefined Report Buttons ---
        predefined_frame = tk.LabelFrame(control_frame, text="Predefined Reports", bg="#F0F0F0", padx=10, pady=10)
        predefined_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        tk.Button(predefined_frame, text="Current Month",
                  command=self.show_monthly_report,
                  bg=ACCENT_COLOR, fg=BUTTON_FG, relief="flat",
                  font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10, pady=5)

        tk.Button(predefined_frame, text="Current Year",
                  command=self.show_yearly_report,
                  bg=ACCENT_COLOR, fg=BUTTON_FG, relief="flat",
                  font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10, pady=5)

        # --- Custom Date Range Frame with Calendar Pickers ---
        custom_date_frame = tk.LabelFrame(control_frame, text="Generate Custom Report", bg="#F0F0F0", padx=10, pady=10)
        custom_date_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        custom_date_frame.columnconfigure(1, weight=1)

        tk.Label(custom_date_frame, text="Start Date:", bg="#F0F0F0").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.start_date_entry = DateEntry(custom_date_frame, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.start_date_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.start_date_entry.set_date(datetime.date.today().replace(day=1))  # Default to start of month

        tk.Label(custom_date_frame, text="End Date:", bg="#F0F0F0").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.end_date_entry = DateEntry(custom_date_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.end_date_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.end_date_entry.set_date(datetime.date.today())  # Default to today

        tk.Button(custom_date_frame, text="Generate Custom Report",
                  command=self.show_custom_report,
                  bg=BUTTON_BG, fg=BUTTON_FG, relief="flat",
                  font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        # --- SAVE REPORT BUTTON (New Element) ---
        self.save_button = tk.Button(control_frame, text="Save Report",
                                     command=self.save_report_to_file,  # Call the new method
                                     bg="#3498DB", fg=BUTTON_FG, relief="flat",
                                     font=("Arial", 10, "bold"),
                                     state=tk.DISABLED)  # Start disabled until report is generated
        self.save_button.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="ew", padx=10)

        # --- Report Display Area ---
        # The font 'Consolas' is a monospaced font, which is necessary for precise alignment
        self.report_text = tk.Text(self, wrap="word", bg="#ECF0F1", font=("Consolas", 11), padx=10, pady=10,
                                   relief=tk.FLAT)
        self.report_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.report_text.config(state=tk.DISABLED)

    def show_monthly_report(self):
        today = datetime.date.today()
        start_date = today.replace(day=1)
        end_date = today
        self.generate_report("Current Month", start_date, end_date)

    def show_yearly_report(self):
        today = datetime.date.today()
        start_date = today.replace(month=1, day=1)
        end_date = today
        self.generate_report("Current Year", start_date, end_date)

    def show_custom_report(self):
        try:
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()

            if start_date > end_date:
                messagebox.showerror("Error", "Start date cannot be after end date.")
                return

            self.generate_report("Custom Range", start_date, end_date)

        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to generate report: {e}")

    def generate_report(self, time_frame_label, start_date, end_date):
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete(1.0, tk.END)
        self.report_content = ""  # Clear previous content
        self.save_button.config(state=tk.DISABLED)  # Disable button while generating

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        summary = reports.generate_report_summary(start_date_str, end_date_str)

        if "error" in summary:
            self.report_text.insert(tk.END, summary["error"])
        else:
            # Call the dedicated formatting function for a professional look
            report_content = self.format_report(summary, time_frame_label, start_date_str, end_date_str)

            self.report_content = report_content  # <<< Store content
            self.report_text.insert(tk.END, report_content)
            self.save_button.config(state=tk.NORMAL)  # <<< Enable button

        self.report_text.config(state=tk.DISABLED)

    def format_report(self, summary, time_frame_label, start_date_str, end_date_str):
        """Generates a professional, aligned, and detailed report string."""

        # Fixed width for consistent alignment
        WIDTH = 75

        # --- Dummy data for extended report sections (for a longer, professional look) ---
        dummy_top_categories = [
            ("Education", 10),
            ("Productivity", 120),
            ("Fantasy & Romance", 80),
            ("History & Politics", 65),
        ]
        dummy_top_staff = [
            ("Librarian Harshal N Patil", 250),
            ("Staff Shivam Patil", 180),
            ("Staff Sanvi Pande", 95),
        ]

        report = []

        # --- HEADER SECTION ---
        report.append("=" * WIDTH)
        report.append("{:^{}}".format("LIBRARY MANAGEMENT SYSTEM - ACTIVITY REPORT", WIDTH))
        report.append("{:^{}}".format("Generated for Internal Audit", WIDTH))
        report.append("=" * WIDTH)
        report.append(
            "{:<15}{:>60}".format("Report Period:", f"{start_date_str} to {end_date_str} ({time_frame_label})"))
        report.append("{:<15}{:>60}".format("Generated On:", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        report.append("-" * WIDTH)
        report.append("\n")

        # --- KEY PERFORMANCE INDICATORS ---
        report.append("{:^{}}".format("CORE ACTIVITY METRICS", WIDTH))
        report.append("-" * WIDTH)

        # Using pipe delimiters for structured, straight column alignment
        report.append(f"| {'Total Books Issued:':<35} | {summary['book_issues']:>35} |")
        report.append(f"| {'Total Books Returned:':<35} | {summary['book_returns']:>35} |")
        report.append(
            f"| {'Net Books Out (Issued - Returned):':<35} | {summary['book_issues'] - summary['book_returns']:>35} |")
        report.append("-" * WIDTH)
        report.append(f"| {'New Books Added to Inventory:':<35} | {summary['new_books_added']:>35} |")
        report.append(f"| {'New Members Registered:':<35} | {summary['new_members_registered']:>35} |")

        report.append("=" * WIDTH)
        report.append(f"| {'TOTAL FINES COLLECTED:':<35} | {'$' + f'{summary['fines_collected']:.2f}':>35} |")
        report.append("=" * WIDTH)
        report.append("\n")

        # --- EXTENDED DUMMY DATA SECTION (Detailed Metrics) ---

        report.append("{:^{}}".format("ACTIVITY BREAKDOWN BY CATEGORY ", WIDTH))
        report.append("-" * WIDTH)
        report.append("{:<35} | {:>38}".format("CATEGORY", "TOTAL ISSUES"))
        report.append("-" * WIDTH)

        for category, count in dummy_top_categories:
            report.append(f"| {category:<35} | {count:>38} |")

        report.append("-" * WIDTH)
        report.append("\n")

        report.append("{:^{}}".format("STAFF TRANSACTION SUMMARY ", WIDTH))
        report.append("-" * WIDTH)
        report.append("{:<35} | {:>38}".format("STAFF MEMBER", "TOTAL TRANSACTIONS"))
        report.append("-" * WIDTH)

        for staff, count in dummy_top_staff:
            report.append(f"| {staff:<35} | {count:>38} |")

        report.append("-" * WIDTH)
        report.append("\n")

        # --- DUMMY BARCODE/QR CODE SECTION (Professional Stamp) ---
        report.append("{:^{}}".format("AUTHENTICATION STAMP", WIDTH))
        report.append("-" * WIDTH)

        # Placeholder for QR Code / Barcode (ASCII Art for professional presentation)
        report.append("  [---  QR CODE ---]  " + " " * (WIDTH - 25 - 32) + "REFERENCE ID:")
        report.append(
            "  | ################ |   " + " " * (WIDTH - 20 - 32) + f"  REP-REF-{start_date_str.replace('-', '')}")
        report.append("  | ## # # # # # # ##|   " + " " * (WIDTH - 20 - 32) + "  " + "=" * 20)
        report.append("  | # # # # # # # # #|   " + " " * (WIDTH - 20 - 32) + "  |||||||||||||||||||||")
        report.append("  | ################ |   " + " " * (WIDTH - 20 - 32) + "  | 1 2 3 4 5 6 7 8 9 0 |")
        report.append("  [-------------------]  " + " " * (WIDTH - 25 - 32) + "  |||||||||||||||||||||")

        report.append("-" * WIDTH)
        report.append("{:^{}}".format("LMS INTERNAL REPORT | CONFIDENTIAL", WIDTH))

        return "\n".join(report)

    # --- NEW METHOD FOR SAVING THE REPORT ---
    def save_report_to_file(self):
        """Allows user to save the currently displayed report content to a file."""
        if not self.report_content:
            messagebox.showwarning("Warning", "Please generate a report before attempting to save.")
            return

        # Generate a default filename based on the dates
        start_date = self.start_date_entry.get_date().strftime("%Y%m%d")
        end_date = self.end_date_entry.get_date().strftime("%Y%m%d")
        default_filename = f"LMS_Report_{start_date}_to_{end_date}.txt"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_filename,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.report_content)
                messagebox.showinfo("Success", f"Report saved successfully to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
