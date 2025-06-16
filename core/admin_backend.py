import os
import shutil
import bcrypt
import logging
from datetime import datetime
from .utils import read_csv, write_csv, append_csv, normalize
from .constants import *

def log_action(action, detail=""):
    append_csv(LOGS_CSV, {
        "Timestamp": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "Action": action,
        "Detail": detail
    }, ["Timestamp", "Action", "Detail"])

class AdminBackend:
    @staticmethod
    def get_users():
        return read_csv(USERS_CSV, ["username", "password", "role"])

    @staticmethod
    def add_user(username, password, role):
        users = AdminBackend.get_users()
        if any(u["username"] == username for u in users):
            return False, "Username already exists."
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        append_csv(USERS_CSV, {"username": username, "password": hashed.decode('utf-8'), "role": role}, ["username", "password", "role"])
        log_action("Add User", f"{username} ({role})")
        return True, "User added."

    @staticmethod
    def remove_user(username):
        users = AdminBackend.get_users()
        users = [u for u in users if u["username"] != username]
        write_csv(USERS_CSV, users, ["username", "password", "role"])
        log_action("Remove User", username)
        return True

    @staticmethod
    def reset_password(username, new_password):
        users = AdminBackend.get_users()
        for u in users:
            if u["username"] == username:
                u["password"] = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        write_csv(USERS_CSV, users, ["username", "password", "role"])
        log_action("Reset Password", username)
        return True

    @staticmethod
    def get_students():
        return read_csv(STUDENTS_CSV, ["PRN", "Name", "Class", "Division", "Batch"])

    @staticmethod
    def add_student(student):
        append_csv(STUDENTS_CSV, student, ["PRN", "Name", "Class", "Division", "Batch"])
        log_action("Add Student", student["PRN"])
        return True

    @staticmethod
    def remove_student(student_prn):
        students = AdminBackend.get_students()
        students = [s for s in students if s["PRN"] != student_prn]
        write_csv(STUDENTS_CSV, students, ["PRN", "Name", "Class", "Division", "Batch"])
        log_action("Remove Student", student_prn)
        return True

    @staticmethod
    def get_attendance_files():
        return [f for f in os.listdir(ATTENDANCE_DIR) if f.endswith(".csv")]

    @staticmethod
    def read_attendance(file):
        return read_csv(os.path.join(ATTENDANCE_DIR, file))

    @staticmethod
    def export_attendance(file, export_path):
        shutil.copy(os.path.join(ATTENDANCE_DIR, file), export_path)
        log_action("Export Attendance", file)

    @staticmethod
    def get_face_folders():
        return [name for name in os.listdir(FACE_DATASET_DIR) if os.path.isdir(os.path.join(FACE_DATASET_DIR, name))]

    @staticmethod
    def add_face_folder(folder_path):
        if not os.path.isdir(folder_path):
            return False, "Selected path is not a folder."
        folder_name = os.path.basename(folder_path.rstrip(os.sep))
        dest_path = os.path.join(FACE_DATASET_DIR, folder_name)
        if os.path.exists(dest_path):
            return False, "Folder already exists for this student."
        shutil.copytree(folder_path, dest_path)
        log_action("Add Face Folder", folder_name)
        # retrain_model() # Add your model retrain logic here if needed
        # update_labels_csv()
        return True, "Face folder added."

    @staticmethod
    def remove_face_folder(student_folder_name):
        dest_path = os.path.join(FACE_DATASET_DIR, student_folder_name)
        if os.path.exists(dest_path) and os.path.isdir(dest_path):
            shutil.rmtree(dest_path)
            log_action("Remove Face Folder", student_folder_name)
            # retrain_model()
            # update_labels_csv()
            return True
        return False

    @staticmethod
    def rename_face_folder(old_name, new_name):
        old_path = os.path.join(FACE_DATASET_DIR, old_name)
        new_path = os.path.join(FACE_DATASET_DIR, new_name)
        if not os.path.exists(old_path) or os.path.exists(new_path):
            return False, "Invalid folder name or new name already exists."
        os.rename(old_path, new_path)
        log_action("Rename Face Folder", f"{old_name} -> {new_name}")
        # retrain_model()
        # update_labels_csv()
        return True, "Face folder renamed."

    @staticmethod
    def get_timetable_files():
        return [f for f in os.listdir(TIMETABLE_DIR) if f.endswith(".csv")]

    @staticmethod
    def add_timetable_csv(src_path):
        fname = os.path.basename(src_path)
        dest_path = os.path.join(TIMETABLE_DIR, fname)
        shutil.copy(src_path, dest_path)
        log_action("Add Timetable CSV", fname)
        return True

    @staticmethod
    def remove_timetable_csv(fname):
        path = os.path.join(TIMETABLE_DIR, fname)
        if os.path.exists(path):
            os.remove(path)
            log_action("Remove Timetable CSV", fname)
            return True
        return False

    @staticmethod
    def read_timetable_file(fname):
        return read_csv(os.path.join(TIMETABLE_DIR, fname))

    @staticmethod
    def get_settings():
        return read_csv(SETTINGS_CSV, ["key", "value"])

    @staticmethod
    def set_setting(key, value):
        settings = AdminBackend.get_settings()
        for s in settings:
            if s["key"] == key:
                s["value"] = value
                break
        else:
            settings.append({"key": key, "value": value})
        write_csv(SETTINGS_CSV, settings, ["key", "value"])
        log_action("Set Setting", f"{key}={value}")

    @staticmethod
    def send_notification(msg):
        append_csv(NOTIFICATIONS_CSV, {
            "timestamp": datetime.now().isoformat(sep=" ", timespec="seconds"),
            "message": msg
        }, ["timestamp", "message"])
        log_action("Send Notification", msg)

    @staticmethod
    def get_notifications():
        return read_csv(NOTIFICATIONS_CSV, ["timestamp", "message"])

    @staticmethod
    def get_logs():
        return read_csv(LOGS_CSV, ["Timestamp", "Action", "Detail"])

    @staticmethod
    def write_csv(filepath, rows, headers):
        write_csv(filepath, rows, headers)