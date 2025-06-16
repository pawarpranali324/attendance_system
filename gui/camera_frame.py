import tkinter as tk
from PIL import Image, ImageTk
import cv2
import joblib
import csv
import pandas as pd
from datetime import datetime, timedelta
from core.constants import *
from core.attendance_logging import log_attendance
from core.utils import normalize, time_in_range
import logging
from ultralytics import YOLO
from deepface import DeepFace

class CameraFrame(tk.Frame):
    def __init__(self, master, width=480, height=320):
        super().__init__(master, bg="#181C1F")
        self.width = width
        self.height = height
        self.csv_folder = ATTENDANCE_DIR
        self.session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file = os.path.join(self.csv_folder, f"final_attendance_report_{self.session_time}.csv")
        self.face_confirm_count = 5
        self.time_window = timedelta(minutes=2)
        self.threshold = 0.2

        if not os.path.exists(YOLO_MODEL_PATH):
            raise FileNotFoundError("YOLO model file missing")
        if not os.path.exists(SVM_MODEL_PATH):
            raise FileNotFoundError("SVM model file missing")

        self.yolo_model = YOLO(YOLO_MODEL_PATH)
        self.clf = joblib.load(SVM_MODEL_PATH)
        self.student_info = {}
        self.students = {}
        try:
            if os.path.exists(STUDENTS_CSV):
                df_students = pd.read_csv(STUDENTS_CSV, dtype=str).fillna("")
                for _, row in df_students.iterrows():
                    prn = str(row["PRN"]).strip()
                    self.students[normalize(prn)] = row
                    self.students[normalize(row.get("Name", ""))] = row
                    self.student_info[normalize(prn)] = {
                        "Sr No.": "",
                        "PRN": prn,
                        "Student Name": row.get("Name", ""),
                        "Class": row.get("Class", ""),
                        "Division": row.get("Division", ""),
                        "Batch": row.get("Batch", ""),
                        "Label": prn
                    }
        except Exception as e:
            logging.error(f"Error loading students.csv: {e}")

        self.timetable = []
        try:
            if os.path.exists(TIMETABLE_CSV):
                df_tt = pd.read_csv(TIMETABLE_CSV, dtype=str).fillna("")
                for _, row in df_tt.iterrows():
                    self.timetable.append({
                        "Day": normalize(row.get("Day", "")),
                        "Time": row.get("Time", ""),
                        "Division": normalize(row.get("Division", "")),
                        "Batch": normalize(row.get("Batch", "")),
                        "Subject": row.get("Subject", ""),
                        "Faculty": row.get("Faculty", "")
                    })
        except Exception as e:
            logging.error(f"Error loading timetable.csv: {e}")

        try:
            with open(self.csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Sr No.", "PRN", "Student Name", "Class", "Division", "Time", "Date", "Day", "Subject", "Faculty"])
        except Exception as e:
            logging.error(f"Error creating attendance CSV: {e}")

        self.recognition_counter = {}
        self.last_logged_times = {}
        self.row_counter = 1
        self.cap = cv2.VideoCapture(0)
        self.label = tk.Label(self, bg="#181C1F")
        self.label.pack()
        self.names_label = tk.Label(self, bg="#181C1F", fg="#00FF99", font=("Segoe UI", 13))
        self.names_label.pack()
        self.running = True
        self.imgtk = None
        self.after(0, self.update_frame)

    def match_timetable_for_student(self, student, ts):
        if not student or not self.timetable:
            return {}
        day = normalize(ts.strftime("%A"))
        time_now = ts.strftime("%H:%M")
        student_div = normalize(student.get("Division", ""))
        student_batch = normalize(student.get("Batch", ""))
        for row in self.timetable:
            row_day = normalize(row.get("Day", ""))
            row_div = normalize(row.get("Division", ""))
            row_batch = normalize(row.get("Batch", ""))
            if row_day != day or row_div != student_div or (row_batch and row_batch != student_batch):
                continue
            if time_in_range(time_now, row["Time"]):
                return row
        return {}

    def update_frame(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        recognized_names = []
        if ret:
            try:
                results = self.yolo_model(frame)[0]
                boxes = results.boxes.xyxy.cpu().numpy().astype(int) if results.boxes.xyxy.numel() else []
                for (x1, y1, x2, y2) in boxes:
                    face_img = frame[y1:y2, x1:x2]
                    label = "Unknown"
                    color = (0, 0, 255)
                    try:
                        embedding = DeepFace.represent(img_path=face_img, model_name="ArcFace", enforce_detection=False)[0]["embedding"]
                        prediction = self.clf.predict([embedding])[0]
                        prob = self.clf.predict_proba([embedding])[0].max()
                        if prob >= self.threshold:
                            label = str(prediction).strip()
                            color = (0, 255, 0)
                            key = normalize(label)
                            self.recognition_counter[key] = self.recognition_counter.get(key, 0) + 1
                            if self.recognition_counter[key] == self.face_confirm_count:
                                now = datetime.now()
                                last_time = self.last_logged_times.get(key)
                                if not last_time or now - last_time > self.time_window:
                                    student = self.student_info.get(key, None)
                                    time_str = now.strftime("%H:%M")
                                    date_str = now.strftime("%Y-%m-%d")
                                    day_str = now.strftime("%A")
                                    timetable_row = self.match_timetable_for_student(student, now)
                                    subject = timetable_row.get("Subject", "") if timetable_row else ""
                                    faculty = timetable_row.get("Faculty", "") if timetable_row else ""
                                    if student:
                                        row = [
                                            self.row_counter, student["PRN"], student["Student Name"],
                                            student["Class"], student["Division"], time_str, date_str,
                                            day_str, subject, faculty
                                        ]
                                        self.row_counter += 1
                                        log_attendance(self.csv_file, student["PRN"], student["Student Name"], self.students, self.timetable)
                                    self.last_logged_times[key] = now
                        else:
                            label = "Unknown"
                            color = (0, 0, 255)
                    except Exception as e:
                        logging.error(f"Face recognition error: {e}")
                        label = "Unknown"
                        color = (0, 0, 255)

                    recognized_names.append(label)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                frame = cv2.resize(frame, (self.width, self.height))
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                self.imgtk = ImageTk.PhotoImage(image=img)
                self.label.configure(image=self.imgtk)

                if recognized_names:
                    self.names_label.config(text="Recognized: " + ", ".join(set(recognized_names)))
                else:
                    self.names_label.config(text="No recognized faces.")
            except Exception as e:
                logging.error(f"Error in update_frame: {e}")
        self.after(30, self.update_frame)

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()