import os
import csv
import logging
from datetime import datetime
from .utils import normalize, time_in_range

def log_attendance(log_file_path, prn, student_name, students, timetable):
    try:
        now = datetime.now()
        day = now.strftime("%A")
        date_val = now.strftime("%Y-%m-%d")
        time_val = now.strftime("%H:%M")
        student = students.get(normalize(prn)) or students.get(normalize(student_name)) or {}
        class_ = student.get("Class", "")
        division = student.get("Division", "")
        batch = student.get("Batch", "")
        subject_val = ""
        faculty_val = ""
        for ttr in timetable:
            if (
                normalize(ttr.get("Day", "")) == normalize(day)
                and normalize(ttr.get("Division", "")) == normalize(division)
                and normalize(ttr.get("Batch", "")) == normalize(batch)
                and time_in_range(time_val, ttr.get("Time", ""))
            ):
                subject_val = ttr.get("Subject", "")
                faculty_val = ttr.get("Faculty", "")
                break
        with open(log_file_path, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "", student.get("PRN", ""), student_name, class_, division,
                time_val, date_val, day, subject_val, faculty_val
            ])
    except Exception as e:
        logging.error(f"Error logging attendance: {e}")

def cleanup_old_logs(log_dir, days=30):
    try:
        now = datetime.now()
        for f in os.listdir(log_dir):
            if f.endswith(".csv"):
                path = os.path.join(log_dir, f)
                file_time = datetime.fromtimestamp(os.path.getmtime(path))
                if (now - file_time).days > days:
                    os.remove(path)
    except Exception as e:
        logging.error(f"Error cleaning old logs: {e}")