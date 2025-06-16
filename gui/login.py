import tkinter as tk
from tkinter import messagebox, simpledialog
import bcrypt
from core.admin_backend import AdminBackend

class LoginScreen(tk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master, bg="#23272E")
        self.master = master
        self.on_login = on_login
        tk.Label(self, text="AI Attendance System", fg="#00FF99", bg="#23272E", font=("Segoe UI", 22, "bold")).pack(pady=24)
        tk.Label(self, text="Login as:", fg="#00FF99", bg="#23272E", font=("Segoe UI", 15)).pack(pady=8)
        self.role = tk.StringVar()
        role_frame = tk.Frame(self, bg="#23272E")
        role_frame.pack(pady=6)
        tk.Radiobutton(role_frame, text="Owner/Admin", variable=self.role, value="owner", font=("Segoe UI", 13), bg="#23272E", fg="white", selectcolor="#00FF99").pack(side=tk.LEFT, padx=8)
        tk.Radiobutton(role_frame, text="Faculty", variable=self.role, value="faculty", font=("Segoe UI", 13), bg="#23272E", fg="white", selectcolor="#00FF99").pack(side=tk.LEFT, padx=8)
        tk.Label(self, text="Username:", fg="white", bg="#23272E", font=("Segoe UI", 12)).pack(pady=6)
        self.username_entry = tk.Entry(self, font=("Segoe UI", 12), width=18)
        self.username_entry.pack()
        tk.Label(self, text="Password:", fg="white", bg="#23272E", font=("Segoe UI", 12)).pack(pady=6)
        self.password_entry = tk.Entry(self, show="*", font=("Segoe UI", 12), width=18)
        self.password_entry.pack()
        self.show_pw_var = tk.BooleanVar(value=False)
        show_pw_cb = tk.Checkbutton(self, text="Show Password", variable=self.show_pw_var, bg="#23272E", fg="#00FF99", activebackground="#23272E", selectcolor="#23272E", command=self.toggle_password)
        show_pw_cb.pack()
        btn_frame = tk.Frame(self, bg="#23272E")
        btn_frame.pack(pady=18)
        tk.Button(btn_frame, text="Login", font=("Segoe UI", 12, "bold"), bg="#00FF99", fg="#23272E", width=10, command=self.try_login).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Sign Up", font=("Segoe UI", 12, "bold"), bg="#4444FF", fg="white", width=10, command=self.open_signup).pack(side=tk.LEFT, padx=6)

    def toggle_password(self):
        if self.show_pw_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def try_login(self):
        role = self.role.get()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not role or not username or not password:
            messagebox.showwarning("Login", "Please fill all fields and select a role.")
            return
        # Validate login
        users = AdminBackend.get_users()
        for user in users:
            if user["username"] == username and user["role"] == role:
                if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                    self.on_login(role, username)
                    return
        messagebox.showerror("Login", "Invalid username, password, or role.")

    def open_signup(self):
        from gui.signup import SignUpDialog
        SignUpDialog(self.master)