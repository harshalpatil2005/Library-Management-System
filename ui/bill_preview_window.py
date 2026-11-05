import tkinter as tk
from tkinter import messagebox, filedialog
import datetime

class BillPreviewWindow(tk.Toplevel):
    def __init__(self, parent, bill_content, default_filename):
        super().__init__(parent)
        self.parent = parent
        self.bill_content = bill_content
        self.default_filename = default_filename
        self.title("Bill Preview")
        self.geometry("600x500")

        self.create_widgets()

    def create_widgets(self):
        # Frame to hold the bill content
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Text widget to show the bill content
        self.bill_text = tk.Text(content_frame, wrap="word", font=("Courier", 12))
        self.bill_text.insert(tk.END, self.bill_content)
        self.bill_text.config(state="disabled") # Make it read-only
        self.bill_text.pack(side="left", fill="both", expand=True)

        # Scrollbar for the text widget
        scrollbar = tk.Scrollbar(content_frame, command=self.bill_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.bill_text.config(yscrollcommand=scrollbar.set)

        # Button to save the bill
        self.save_button = tk.Button(self, text="Save Bill", command=self.save_bill)
        self.save_button.pack(pady=10)

    def save_bill(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                initialfile=self.default_filename,
                title="Save Bill"
            )
            if file_path:
                with open(file_path, "w") as f:
                    f.write(self.bill_content)
                messagebox.showinfo("Success", f"Bill saved to {file_path}")
                self.destroy() # Close the preview window
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {e}")