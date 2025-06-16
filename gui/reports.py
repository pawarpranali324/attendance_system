import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import csv
import os
from datetime import datetime
import smtplib
from email.message import EmailMessage
from core.constants import ATTENDANCE_DIR

class ReportsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1F2326")
        tk.Label(self, text="Attendance Full Report (by Subject & Date Range)", font=("Segoe UI", 16, "bold"), bg="#1F2326", fg="#00FF99").pack(pady=10)
        tk.Label(self, text="You can select which attendance log (live streaming) to report on.", bg="#1F2326", fg="#AAA").pack(pady=4)

        form = tk.Frame(self, bg="#1F2326")
        form.pack(pady=10)

        tk.Label(form, text="Subject (leave blank for all):", bg="#1F2326", fg="#FFF").grid(row=0, column=0, sticky="e")
        self.subject_entry = tk.Entry(form)
        self.subject_entry.grid(row=0, column=1)

        tk.Label(form, text="From Date (YYYY-MM-DD):", bg="#1F2326", fg="#FFF").grid(row=1, column=0, sticky="e")
        self.from_date_entry = tk.Entry(form)
        self.from_date_entry.grid(row=1, column=1)

        tk.Label(form, text="To Date (YYYY-MM-DD):", bg="#1F2326", fg="#FFF").grid(row=2, column=0, sticky="e")
        self.to_date_entry = tk.Entry(form)
        self.to_date_entry.grid(row=2, column=1)

        self.exported_path = None

        button_row = tk.Frame(self, bg="#1F2326")
        button_row.pack(pady=12)
        tk.Button(button_row, text="Generate & Export Full Report", command=self.export_report, bg="#00CC99", fg="#FFF").pack(side=tk.LEFT, padx=5)
        tk.Button(button_row, text="Create & Email Report", command=self.create_and_email_report, bg="#4444FF", fg="#FFF").pack(side=tk.LEFT, padx=5)

    def export_report(self, send_after_export=False):
        subject = self.subject_entry.get().strip()
        from_date = self.from_date_entry.get().strip()
        to_date = self.to_date_entry.get().strip()

        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
            to_dt = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None
        except Exception:
            messagebox.showerror("Date format error", "Dates must be in YYYY-MM-DD format.")
            return

        all_files = [os.path.join(ATTENDANCE_DIR, f) for f in os.listdir(ATTENDANCE_DIR) if f.endswith(".csv")]
        merged_rows = []
        header = None
        for file_path in all_files:
            with open(file_path, newline='', encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                if not header and rows:
                    header = rows[0]
                for row in rows[1:]:
                    try:
                        row_date = row[6]
                        row_subject = row[8]
                        row_dt = datetime.strptime(row_date, "%Y-%m-%d")
                        if subject and subject.lower() not in row_subject.lower():
                            continue
                        if from_dt and row_dt < from_dt:
                            continue
                        if to_dt and row_dt > to_dt:
                            continue
                        merged_rows.append(row)
                    except Exception:
                        continue

        if not merged_rows:
            messagebox.showinfo("No data", "No records matched your criteria.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Save Full Report")
        if not save_path:
            return

        try:
            with open(save_path, "w", newline='', encoding="utf-8") as out:
                writer = csv.writer(out)
                writer.writerow(header)
                writer.writerows(merged_rows)
            messagebox.showinfo("Exported", f"Report exported to {save_path}")
            self.exported_path = save_path
            if send_after_export:
                self.send_email(auto_send=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
            self.exported_path = None

    def create_and_email_report(self):
        self.export_report(send_after_export=True)

    def send_email(self, auto_send=False):
        if not self.exported_path or not os.path.exists(self.exported_path):
            messagebox.showerror("No Exported Report", "Please export a report first, then send via email.")
            return

        if auto_send:
            sender_email = "kspsquad4@gmail.com"
            sender_password = "zavp teiy wwmm fcvs"
            recipient = simpledialog.askstring("Recipient Email", "Enter recipient's email address:")
            subject = "Attendance Report"
            body = "Please find attached the attendance report."
        else:
            sender_email = simpledialog.askstring("Your Email", "Enter your email address:")
            sender_password = simpledialog.askstring("Your Email Password", "Enter your email password (app password for Gmail):", show="*")
            recipient = simpledialog.askstring("Recipient Email", "Enter recipient's email address:")
            subject = simpledialog.askstring("Email Subject", "Enter email subject:", initialvalue="Attendance Report")
            body = simpledialog.askstring("Email Body", "Enter email body:", initialvalue="Please find attached the attendance report.")

            if not sender_email or not sender_password or not recipient or not subject or not body:
                messagebox.showerror("Missing Info", "All fields are required.")
                return

        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = recipient
            msg.set_content(body)

            with open(self.exported_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(self.exported_path)
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            messagebox.showinfo("Email sent", f"Report sent to {recipient} successfully.")
        except Exception as e:
            messagebox.showerror("Email Error", f"Failed to send email: {e}")
