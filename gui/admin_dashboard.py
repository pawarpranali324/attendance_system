import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
import csv
from core.admin_backend import AdminBackend
from gui.signup import SignUpDialog
from gui.reports import ReportsFrame
from core.constants import STUDENTS_CSV

def normalize(val):
    return str(val).strip().replace(" ", "").lower()

class AdminDashboard(tk.Frame):
    def __init__(self, master, on_logout):
        super().__init__(master, bg="#23272E")
        self.master = master
        self.on_logout = on_logout
        self.current_page = self.show_dashboard

        sidebar = tk.Frame(self, bg="#181C1F", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        btn_opts = [
            ("Dashboard", self.show_dashboard),
            ("User Management", self.show_user_mgmt),
            ("Student Management", self.show_students),
            ("Attendance", self.show_attendance),
            ("Face Dataset", self.show_face_dataset),
            ("Timetable", self.show_timetable),
            ("Reports", self.show_reports),
            ("Logs & Audit", self.show_logs),
            ("Settings", self.show_settings),
            ("Notifications", self.show_notifications),
            ("Logout", self.logout)
        ]
        self.buttons = []
        for name, cmd in btn_opts:
            btn = tk.Button(
                sidebar, text=name, font=("Segoe UI", 12, "bold"),
                bg="#00FF99" if name == "Dashboard" else "#222",
                fg="#181C1F" if name == "Dashboard" else "#FFF",
                relief=tk.FLAT, command=cmd, height=2
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.buttons.append(btn)
        refresh_btn = tk.Button(
            sidebar, text="Refresh Page", font=("Segoe UI", 12, "bold"),
            bg="#888888", fg="#FFF", relief=tk.FLAT,
            command=lambda: self.current_page() if self.current_page else None, height=2
        )
        refresh_btn.pack(fill=tk.X, padx=10, pady=2)

        self.content = tk.Frame(self, bg="#1F2326")
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.show_dashboard()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.current_page = self.show_dashboard
        self.clear_content()
        tk.Label(
            self.content, text="Admin Dashboard Overview",
            font=("Segoe UI", 18, "bold"),
            bg="#1F2326", fg="#00FF99"
        ).pack(pady=16)
        stats = [
            ("Total Users", len(AdminBackend.get_users())),
            ("Total Students", len(AdminBackend.get_students())),
            ("Attendance Files", len(AdminBackend.get_attendance_files())),
            ("Face Folders (Students)", len(AdminBackend.get_face_folders())),
            ("Timetable Files", len(AdminBackend.get_timetable_files()))
        ]
        for s, v in stats:
            tk.Label(
                self.content, text=f"{s}: {v}", font=("Segoe UI", 13),
                bg="#1F2326", fg="#FFF"
            ).pack(anchor="w", padx=50, pady=2)

    def show_user_mgmt(self):
        self.current_page = self.show_user_mgmt
        self.clear_content()
        tk.Label(self.content, text="User Management", font=("Segoe UI", 16, "bold"), bg="#1F2326", fg="#00FF99").pack(pady=8)
        frm = tk.Frame(self.content, bg="#1F2326")
        frm.pack(pady=4)

        user_table = ttk.Treeview(frm, columns=("username", "role"), show="headings")
        user_table.heading("username", text="Username")
        user_table.heading("role", text="Role")
        users = AdminBackend.get_users()
        for u in users:
            user_table.insert("", "end", values=(u["username"], u["role"]))
        user_table.pack()

        def add_user_popup():
            popup = tk.Toplevel(self)
            popup.title("Add User")
            tk.Label(popup, text="Username:").pack()
            ent_username = tk.Entry(popup)
            ent_username.pack()
            tk.Label(popup, text="Password:").pack()
            ent_password = tk.Entry(popup, show="*")
            ent_password.pack()
            tk.Label(popup, text="Role:").pack()
            ent_role = ttk.Combobox(popup, values=["owner", "faculty"])
            ent_role.pack()
            def add():
                ok, msg = AdminBackend.add_user(ent_username.get(), ent_password.get(), ent_role.get())
                messagebox.showinfo("Add User", msg, parent=popup)
                popup.destroy()
                self.show_user_mgmt()
            tk.Button(popup, text="Add", command=add).pack()

        def remove_user():
            selected = user_table.selection()
            if not selected:
                return
            username = user_table.item(selected[0])["values"][0]
            if messagebox.askyesno("Remove User", f"Remove user {username}?", parent=self):
                AdminBackend.remove_user(username)
                self.show_user_mgmt()

        def reset_password():
            selected = user_table.selection()
            if not selected:
                return
            username = user_table.item(selected[0])["values"][0]
            new_pw = simpledialog.askstring("Reset Password", f"New password for {username}:", show="*")
            if new_pw:
                AdminBackend.reset_password(username, new_pw)
                messagebox.showinfo("Reset Password", "Password reset.")

        tk.Button(frm, text="Add User", command=add_user_popup).pack(side=tk.LEFT, padx=5)
        tk.Button(frm, text="Remove User", command=remove_user).pack(side=tk.LEFT, padx=5)
        tk.Button(frm, text="Reset Password", command=reset_password).pack(side=tk.LEFT, padx=5)

    def show_students(self):
        self.current_page = self.show_students
        self.clear_content()
        tk.Label(self.content, text="Student Management", font=("Segoe UI", 16, "bold"), bg="#1F2326", fg="#00FF99").pack(pady=8)
        frm = tk.Frame(self.content, bg="#1F2326")
        frm.pack(pady=4, fill=tk.BOTH, expand=True)

        columns = ("PRN", "Name", "Class", "Division", "Batch")
        self.tree = ttk.Treeview(frm, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        def refresh_table():
            for i in self.tree.get_children():
                self.tree.delete(i)
            students = AdminBackend.get_students()
            for s in students:
                self.tree.insert("", "end", values=(s["PRN"], s["Name"], s["Class"], s["Division"], s["Batch"]))

        refresh_table()

        def add_student_popup():
            popup = tk.Toplevel(self)
            popup.title("Add Student")
            popup.geometry("340x340")
            tk.Label(popup, text="PRN:").pack()
            ent_prn = tk.Entry(popup)
            ent_prn.pack()
            tk.Label(popup, text="Name:").pack()
            ent_name = tk.Entry(popup)
            ent_name.pack()
            tk.Label(popup, text="Class:").pack()
            ent_class = tk.Entry(popup)
            ent_class.pack()
            tk.Label(popup, text="Division:").pack()
            ent_div = tk.Entry(popup)
            ent_div.pack()
            tk.Label(popup, text="Batch:").pack()
            ent_batch = tk.Entry(popup)
            ent_batch.pack()

            def add():
                sprn = ent_prn.get().strip()
                sname = ent_name.get().strip()
                sclass = ent_class.get().strip()
                sdiv = ent_div.get().strip()
                sbatch = ent_batch.get().strip()
                if not sprn or not sname:
                    messagebox.showerror("Add Student", "PRN and Name are required.", parent=popup)
                    return
                AdminBackend.add_student({
                    "PRN": sprn, "Name": sname, "Class": sclass, "Division": sdiv, "Batch": sbatch
                })
                messagebox.showinfo("Add Student", "Student added.", parent=popup)
                popup.destroy()
                refresh_table()

            tk.Button(popup, text="Add", command=add).pack(pady=8)

        def remove_student():
            selected = self.tree.selection()
            if not selected:
                return
            student_prn = self.tree.item(selected[0])["values"][0]
            if messagebox.askyesno("Remove Student", "Are you sure you want to remove this student?"):
                AdminBackend.remove_student(student_prn)
                messagebox.showinfo("Remove Student", "Student removed.")
                refresh_table()

        def edit_student_popup():
            selected = self.tree.selection()
            if not selected:
                return
            s = self.tree.item(selected[0])["values"]
            popup = tk.Toplevel(self)
            popup.title("Edit Student")
            popup.geometry("340x340")
            tk.Label(popup, text="PRN (cannot edit):").pack()
            ent_prn = tk.Entry(popup)
            ent_prn.insert(0, s[0])
            ent_prn.config(state="disabled")
            ent_prn.pack()
            tk.Label(popup, text="Name:").pack()
            ent_name = tk.Entry(popup)
            ent_name.insert(0, s[1])
            ent_name.pack()
            tk.Label(popup, text="Class:").pack()
            ent_class = tk.Entry(popup)
            ent_class.insert(0, s[2])
            ent_class.pack()
            tk.Label(popup, text="Division:").pack()
            ent_div = tk.Entry(popup)
            ent_div.insert(0, s[3])
            ent_div.pack()
            tk.Label(popup, text="Batch:").pack()
            ent_batch = tk.Entry(popup)
            ent_batch.insert(0, s[4])
            ent_batch.pack()

            def save():
                sprn = ent_prn.get().strip()
                sname = ent_name.get().strip()
                sclass = ent_class.get().strip()
                sdiv = ent_div.get().strip()
                sbatch = ent_batch.get().strip()
                students = AdminBackend.get_students()
                students = [st for st in students if st["PRN"] != sprn]
                students.append({
                    "PRN": sprn, "Name": sname, "Class": sclass, "Division": sdiv, "Batch": sbatch
                })
                AdminBackend.write_csv(STUDENTS_CSV, students, ["PRN", "Name", "Class", "Division", "Batch"])
                messagebox.showinfo("Edit Student", "Student updated.", parent=popup)
                popup.destroy()
                refresh_table()

            tk.Button(popup, text="Save", command=save).pack(pady=8)

        def import_students_csv():
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], title="Select Students Info CSV")
            if not file_path:
                return

            def get_any_key(d, *keys):
                for k in keys:
                    for dk in d:
                        if normalize(dk) == normalize(k):
                            return d[dk]
                return ""

            try:
                with open(file_path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    imported_rows = []
                    for row in reader:
                        imported_row = {
                            "PRN": get_any_key(row, "PRN", "ID"),
                            "Name": get_any_key(row, "Name"),
                            "Class": get_any_key(row, "Class"),
                            "Division": get_any_key(row, "Division"),
                            "Batch": get_any_key(row, "Batch")
                        }
                        if imported_row["PRN"] and imported_row["Name"]:
                            imported_rows.append(imported_row)
                if not imported_rows:
                    messagebox.showerror("Import Students CSV", "No valid rows found in selected CSV.")
                    return
                students = AdminBackend.get_students()
                existing_prns = set(s["PRN"] for s in students)
                new_rows = [row for row in imported_rows if row["PRN"] not in existing_prns]
                students.extend(new_rows)
                AdminBackend.write_csv(STUDENTS_CSV, students, ["PRN", "Name", "Class", "Division", "Batch"])
                messagebox.showinfo("Import Students CSV", f"Imported {len(new_rows)} new students.")
                refresh_table()
            except Exception as e:
                messagebox.showerror("Import Students CSV", f"Failed to import: {e}")

        btn_frame = tk.Frame(self.content, bg="#1F2326")
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Add Student", command=add_student_popup, bg="#4444FF", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="Edit Student", command=edit_student_popup, bg="#00CC99", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="Remove Student", command=remove_student, bg="#FF4444", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="Import Students CSV", command=import_students_csv, bg="#888888", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)

    def show_attendance(self):
        self.current_page = self.show_attendance
        self.clear_content()
        tk.Label(self.content, text="Attendance Management", font=("Segoe UI", 16, "bold"), bg="#1F2326", fg="#00FF99").pack(pady=8)
        files = AdminBackend.get_attendance_files()
        file_list = tk.Listbox(self.content, height=8)
        for f in files:
            file_list.insert(tk.END, f)
        file_list.pack()

        def view_file():
            idx = file_list.curselection()
            if not idx:
                return
            data = AdminBackend.read_attendance(files[idx[0]])
            win = tk.Toplevel(self)
            win.title("Attendance Records")
            if not data:
                tk.Label(win, text="No attendance data.").pack()
                return
            table = ttk.Treeview(win, columns=list(data[0].keys()), show="headings")
            for k in data[0].keys():
                table.heading(k, text=k)
            for row in data:
                table.insert("", "end", values=[row[k] for k in row])
            table.pack(expand=True, fill=tk.BOTH)

        def export_file():
            idx = file_list.curselection()
            if not idx:
                return
            file = files[idx[0]]
            dest = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if dest:
                AdminBackend.export_attendance(file, dest)
                messagebox.showinfo("Export", f"Exported to {dest}")

        tk.Button(self.content, text="View Attendance", command=view_file).pack(pady=2)
        tk.Button(self.content, text="Export Attendance", command=export_file).pack(pady=2)

    def show_face_dataset(self):
        self.current_page = self.show_face_dataset
        self.clear_content()
        tk.Label(self.content, text="Face Dataset Management (by Student Folder)", font=("Segoe UI", 16, "bold"), bg="#1F2326", fg="#00FF99").pack(pady=8)
        folders = AdminBackend.get_face_folders()
        folder_list = tk.Listbox(self.content, height=12)
        for f in folders:
            folder_list.insert(tk.END, f)
        folder_list.pack(pady=2, fill=tk.X, padx=16)

        def add_folder():
            folder_path = filedialog.askdirectory(title="Select Student Face Folder")
            if folder_path:
                ok, msg = AdminBackend.add_face_folder(folder_path)
                if ok:
                    messagebox.showinfo("Add Face Folder", msg)
                else:
                    messagebox.showerror("Add Face Folder", msg)
                self.show_face_dataset()

        def add_folders_batch():
            parent_folder = filedialog.askdirectory(title="Select Parent Folder Containing Student Folders")
            if not parent_folder:
                return
            subfolders = [os.path.join(parent_folder, name) for name in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, name))]
            added = 0
            skipped = 0
            for sub in subfolders:
                ok, msg = AdminBackend.add_face_folder(sub)
                if ok:
                    added += 1
                else:
                    skipped += 1
            messagebox.showinfo("Batch Add", f"Added {added} folders, skipped {skipped} (already existed).")
            self.show_face_dataset()

        def remove_folder():
            idx = folder_list.curselection()
            if not idx:
                return
            student_folder = folders[idx[0]]
            if messagebox.askyesno("Remove Face Folder", f"Remove folder for '{student_folder}' and all images inside?"):
                AdminBackend.remove_face_folder(student_folder)
                self.show_face_dataset()

        btn_frame = tk.Frame(self.content, bg="#1F2326")
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Add Face Folder", command=add_folder, bg="#4444FF", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="Batch Add Folders", command=add_folders_batch, bg="#00CC99", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="Remove Face Folder", command=remove_folder, bg="#FF4444", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)

    def show_timetable(self):
        self.current_page = self.show_timetable
        self.clear_content()
        tk.Label(self.content, text="Timetable Management", font=("Segoe UI", 16, "bold"), bg="#1F2326", fg="#00FF99").pack(pady=8)
        files = AdminBackend.get_timetable_files()
        file_list = tk.Listbox(self.content, height=8, selectmode=tk.SINGLE)
        for f in files:
            file_list.insert(tk.END, f)
        file_list.pack(pady=2, fill=tk.X, padx=16)

        def import_csv():
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if file_path:
                AdminBackend.add_timetable_csv(file_path)
                self.show_timetable()
                messagebox.showinfo("Import Timetable", f"Timetable CSV '{os.path.basename(file_path)}' imported.")

        def view_timetable():
            idx = file_list.curselection()
            if not idx:
                return
            fname = files[idx[0]]
            data = AdminBackend.read_timetable_file(fname)
            win = tk.Toplevel(self)
            win.title(f"View Timetable: {fname}")
            if not data:
                tk.Label(win, text="No data to display.").pack()
                return
            columns = list(data[0].keys())
            table = ttk.Treeview(win, columns=columns, show="headings")
            for col in columns:
                table.heading(col, text=col)
            for row in data:
                table.insert("", "end", values=[row[c] for c in columns])
            table.pack(expand=True, fill=tk.BOTH)

        def remove_timetable():
            idx = file_list.curselection()
            if not idx:
                return
            fname = files[idx[0]]
            if messagebox.askyesno("Remove Timetable", f"Delete timetable file '{fname}'?"):
                AdminBackend.remove_timetable_csv(fname)
                self.show_timetable()

        btn_frame = tk.Frame(self.content, bg="#1F2326")
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Import Timetable CSV", command=import_csv, bg="#4444FF", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="View Timetable", command=view_timetable, bg="#4444FF", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="Remove Timetable", command=remove_timetable, bg="#FF4444", fg="#FFF", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=3)

    def show_reports(self):
        self.current_page = self.show_reports
        self.clear_content()
        ReportsFrame(self.content).pack(fill="both", expand=True)

    def show_logs(self):
        self.current_page = self.show_logs
        self.clear_content()
        tk.Label(self.content, text="Logs & Audit", font=("Segoe UI", 16, "bold"), bg="#1F2326", fg="#00FF99").pack(pady=8)
        logs = AdminBackend.get_logs()
        table = ttk.Treeview(self.content, columns=["Timestamp", "Action", "Detail"], show="headings")
        for c in ["Timestamp", "Action", "Detail"]:
            table.heading(c, text=c)
        for row in logs[-100:]:
            table.insert("", "end", values=(row["Timestamp"], row["Action"], row["Detail"]))
        table.pack(expand=True, fill=tk.BOTH)

    def show_settings(self):
        self.current_page = self.show_settings
        self.clear_content()
        tk.Label(self.content, text="System Settings", font=("Segoe UI", 16, "bold"), bg="#1F2326", fg="#00FF99").pack(pady=8)
        settings = AdminBackend.get_settings()
        frm = tk.Frame(self.content, bg="#1F2326")
        frm.pack()
        table = ttk.Treeview(frm, columns=["key", "value"], show="headings")
        table.heading("key", text="Key")
        table.heading("value", text="Value")
        for row in settings:
            table.insert("", "end", values=(row["key"], row["value"]))
        table.pack()

        def set_setting():
            key = simpledialog.askstring("Setting Key", "Key:")
            value = simpledialog.askstring("Setting Value", "Value:")
            if key and value:
                AdminBackend.set_setting(key, value)
                self.show_settings()
        tk.Button(frm, text="Set Setting", command=set_setting).pack(pady=2)

    def show_notifications(self):
        self.current_page = self.show_notifications
        self.clear_content()
        tk.Label(self.content, text="Notifications", font=("Segoe UI", 16, "bold"), bg="#1F2326", fg="#00FF99").pack(pady=8)
        notifs = AdminBackend.get_notifications()
        table = ttk.Treeview(self.content, columns=["timestamp", "message"], show="headings")
        table.heading("timestamp", text="Timestamp")
        table.heading("message", text="Message")
        for row in notifs[-50:]:
            table.insert("", "end", values=(row["timestamp"], row["message"]))
        table.pack()

        def send_notif():
            msg = simpledialog.askstring("Send Notification", "Message:")
            if msg:
                AdminBackend.send_notification(msg)
                self.show_notifications()
        tk.Button(self.content, text="Send Notification", command=send_notif).pack(pady=2)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.on_logout()