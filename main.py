import tkinter as tk
import logging
from gui.login import LoginScreen
from gui.camera_frame import CameraFrame
from gui.user_status import UserStatusFrame
from core.constants import *
from core.attendance_logging import cleanup_old_logs

class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Attendance System - Face Recognition")
        self.geometry("980x540")
        self.configure(bg="#181C1F")
        cleanup_old_logs(ATTENDANCE_DIR)
        menubar = tk.Menu(self)
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Refresh Admin Dashboard Page", command=self.refresh_current_page)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        self.config(menu=menubar)
        self.admin_dashboard_instance = None

        left_frame = tk.Frame(self, width=340, height=520, bg="#23272E")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(16,8), pady=10)
        left_frame.pack_propagate(False)
        LoginScreen(left_frame, self.on_login).pack(fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(self, width=600, height=520, bg="#181C1F")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(6,18), pady=10)
        right_frame.pack_propagate(False)

        self.camera_frame = CameraFrame(right_frame, width=540, height=400)
        self.camera_frame.pack(pady=(10,8))
        self.status_frame = UserStatusFrame(right_frame, width=540, height=80)
        self.status_frame.pack(pady=(8,10))

    def refresh_current_page(self):
        if self.admin_dashboard_instance and hasattr(self.admin_dashboard_instance, "current_page") and self.admin_dashboard_instance.current_page:
            self.admin_dashboard_instance.current_page()
            tk.messagebox.showinfo("Refreshed", "Current Admin Dashboard page refreshed!")
        else:
            tk.messagebox.showinfo("No Admin Dashboard", "Open Admin Dashboard to refresh a page.")

    def on_login(self, role, username):
        self.status_frame.show_user(username, role)
        tk.messagebox.showinfo("Login", f"Logged in as {username} ({role})")
        # Now open admin dashboard if role is owner
        if role == "owner":
            self.open_admin_dashboard()

    def open_admin_dashboard(self):
        import tkinter as tk  # Needed for Toplevel
        from gui.admin_dashboard import AdminDashboard  # Make sure this import is correct!
        admin_root = tk.Toplevel(self)
        admin_root.geometry("1100x650")
        admin_root.title("Admin Dashboard (Owner/Admin)")
        def logout_and_close():
            admin_root.destroy()
        dashboard = AdminDashboard(admin_root, logout_and_close)
        dashboard.pack(fill=tk.BOTH, expand=True)
        self.admin_dashboard_instance = dashboard
        # (Optional) Add menu for refresh, etc. on admin_root if you want

    def on_closing(self):
        self.camera_frame.stop()
        self.destroy()

if __name__ == "__main__":
    try:
        app = AttendanceApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Application failed to start: {e}")