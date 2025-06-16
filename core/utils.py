import os
import csv
import logging
from datetime import datetime

def normalize(val):
    return str(val).strip().replace(" ", "").lower()

def time_in_range(time_str, range_str):
    try:
        t = datetime.strptime(time_str, "%H:%M").time()
        start, end = range_str.split("-")
        start_t = datetime.strptime(start.strip(), "%H:%M").time()
        end_t = datetime.strptime(end.strip(), "%H:%M").time()
        return start_t <= t <= end_t
    except Exception as e:
        logging.error(f"Time parsing error: {e}")
        return False

def read_csv(filepath, default_headers=None):
    try:
        if not os.path.exists(filepath):
            if default_headers:
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(default_headers)
            return []
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")
        return []

def write_csv(filepath, rows, headers):
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    except Exception as e:
        logging.error(f"Error writing {filepath}: {e}")

def append_csv(filepath, row, headers=None):
    try:
        exists = os.path.exists(filepath)
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers or row.keys())
            if not exists and headers:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        logging.error(f"Error appending to {filepath}: {e}")