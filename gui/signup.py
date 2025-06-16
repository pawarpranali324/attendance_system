import tkinter as tk
from tkinter import messagebox
from core.admin_backend import AdminBackend

class SignUpDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Sign Up")
        self.configure(bg="#23272E")
        self.geometry("320x400")
        self.resizable(False, False)
        tk.Label(self, text="Sign Up", fg="#00FF99", bg="#23272E", font=("Segoe UI", 17, "bold")).pack(pady=18)
        tk.Label(self, text="Username:", fg="white", bg="#23272E", font=("Segoe UI", 12)).pack()
        self.username_entry = tk.Entry(self, font=("Segoe UI", 12), width=16)
        self.username_entry.pack()
        tk.Label(self, text="Password:", fg="white", bg="#23272E", font=("Segoe UI", 12)).pack()
        self.password_entry = tk.Entry(self, show="*", font=("Segoe UI", 12), width=16)
        self.password_entry.pack()
        tk.Label(self, text="Confirm Password:", fg="white", bg="#23272E", font=("Segoe UI", 12)).pack()
        self.conf_password_entry = tk.Entry(self, show="*", font=("Segoe UI", 12), width=16)
        self.conf_password_entry.pack()
        self.show_pw_var = tk.BooleanVar(value=False)
        show_pw_cb = tk.Checkbutton(self, text="Show Passwords", variable=self.show_pw_var, bg="#23272E", fg="#00FF99", activebackground="#23272E", selectcolor="#23272E", command=self.toggle_password)
        show_pw_cb.pack()
        tk.Label(self, text="Role:", fg="white", bg="#23272E", font=("Segoe UI", 12)).pack()
        self.role = tk.StringVar()
        role_frame = tk.Frame(self, bg="#23272E")
        role_frame.pack(pady=4)
        tk.Radiobutton(role_frame, text="Owner/Admin", variable=self.role, value="owner", font=("Segoe UI", 11), bg="#23272E", fg="white", selectcolor="#00FF99").pack(side=tk.LEFT, padx=6)
        tk.Radiobutton(role_frame, text="Faculty", variable=self.role, value="faculty", font=("Segoe UI", 11), bg="#23272E", fg="white", selectcolor="#00FF99").pack(side=tk.LEFT, padx=6)
        btn_frame = tk.Frame(self, bg="#23272E")
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Register", bg="#00FF99", fg="#23272E", font=("Segoe UI", 12, "bold"), width=9, command=self.do_signup).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Cancel", bg="#FF4444", fg="white", font=("Segoe UI", 12, "bold"), width=9, command=self.destroy).pack(side=tk.LEFT, padx=6)
        bottom_frame = tk.Frame(self, bg="#23272E")
        bottom_frame.pack(pady=(12, 3))
        tk.Label(bottom_frame, text="Already registered?", fg="white", bg="#23272E", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        login_link = tk.Label(bottom_frame, text="Login here", fg="#00FF99", bg="#23272E", cursor="hand2", font=("Segoe UI", 10, "underline"))
        login_link.pack(side=tk.LEFT, padx=(3,0))
        login_link.bind("<Button-1>", lambda e: self.destroy())

    def toggle_password(self):
        if self.show_pw_var.get():
            self.password_entry.config(show="")
            self.conf_password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
            self.conf_password_entry.config(show="*")

    def do_signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        conf_password = self.conf_password_entry.get().strip()
        role = self.role.get()
        if not username or not password or not conf_password or not role:
            messagebox.showwarning("Sign Up", "All fields are required.")
            return
        if password != conf_password:
            messagebox.showerror("Sign Up", "Passwords do not match.")
            return
        users = AdminBackend.get_users()
        if any(u["username"] == username for u in users):
            messagebox.showerror("Sign Up", "Username already exists.")
            return
        AdminBackend.add_user(username, password, role)
        messagebox.showinfo("Sign Up", "Registration successful! You may now log in.")
        self.destroy()