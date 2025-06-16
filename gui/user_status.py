import tkinter as tk

class UserStatusFrame(tk.Frame):
    def __init__(self, master, width=400, height=70):
        super().__init__(master, bg="#1F2326", width=width, height=height)
        self.pack_propagate(False)
        self.name_label = tk.Label(self, text="", font=("Segoe UI", 15, "bold"), fg="#00FF99", bg="#1F2326")
        self.name_label.pack(pady=(10,2))
        self.status_label = tk.Label(self, text="", font=("Segoe UI", 12), fg="white", bg="#1F2326")
        self.status_label.pack()

    def show_user(self, username, role):
        self.name_label.config(text=f"Welcome, {username} ({role})")
        self.status_label.config(text="Status: Logged in!")

    def clear(self):
        self.name_label.config(text="")
        self.status_label.config(text="")