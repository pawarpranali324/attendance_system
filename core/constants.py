import os

DATA_DIR = "admin_system_data"
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
STUDENTS_CSV = os.path.join(DATA_DIR, "students.csv")
ATTENDANCE_DIR = os.path.join(DATA_DIR, "face_logs")
TIMETABLE_DIR = os.path.join(DATA_DIR, "timetable")
TIMETABLE_CSV = os.path.join(TIMETABLE_DIR, "timetable.csv")
SETTINGS_CSV = os.path.join(DATA_DIR, "settings.csv")
NOTIFICATIONS_CSV = os.path.join(DATA_DIR, "notifications.csv")
LOGS_CSV = os.path.join(DATA_DIR, "system_logs.csv")
FACE_DATASET_DIR = os.path.join(DATA_DIR, "dataset")
LABELS_CSV = os.path.join(FACE_DATASET_DIR, "labels.csv")
YOLO_MODEL_PATH = "yolov8-face.pt"
SVM_MODEL_PATH = "arcface_svm_recognizer.joblib"

for d in [DATA_DIR, ATTENDANCE_DIR, FACE_DATASET_DIR, TIMETABLE_DIR]:
    os.makedirs(d, exist_ok=True)