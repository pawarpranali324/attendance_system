# AI Attendance System

## Overview

This is a modular, Tkinter-based face recognition attendance system.  
It uses YOLO (Ultralytics) for fast face detection, ArcFace for embeddings, and SVM for classification.  
The system provides a clean admin dashboard for user, student, attendance, timetable, and dataset management, as well as reporting and system logs.

## Features

- Admin/faculty login and signup
- Student and user management
- Real-time face recognition attendance with webcam
- Attendance and timetable CSV management
- Face dataset management (folders, retrain hooks)
- System settings and notifications
- Reporting and audit logs

## Project Structure

```
attendance_system/
├── core/
│   ├── constants.py
│   ├── utils.py
│   ├── attendance_logging.py
│   ├── admin_backend.py
├── gui/
│   ├── login.py
│   ├── signup.py
│   ├── dashboard.py
│   ├── camera_frame.py
│   ├── user_status.py
├── admin_system_data/       # Will be auto-created for data storage
├── yolov8-face.pt           # Place your YOLOv8 face model here
├── arcface_svm_recognizer.joblib # Place your trained SVM here
├── main.py
├── requirements.txt
└── README.md
```

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Download Models:**

   - Place your YOLOv8 face model as `yolov8-face.pt` in the root.
   - Place your trained SVM as `arcface_svm_recognizer.joblib` in the root.

3. **Run the App:**

   ```bash
   python main.py
   ```

4. **Data files** will be created in `admin_system_data/` as you use the system.

## Requirements

See [`requirements.txt`](requirements.txt).

## Notes

- For best performance, use a GPU-enabled machine for DeepFace and YOLO.
- You can retrain or update models by replacing the model files.
- Extend or modify the code in the modular `core/` and `gui/` folders as needed.
