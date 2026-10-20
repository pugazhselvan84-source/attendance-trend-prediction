import os
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "attendance_data.csv"
MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "attendance_trend_prediction")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))

COLUMNS = ["student_id", "student_name", "week", "classes_attended", "total_classes", "attendance_percentage"]

def _mysql_connection():
    if not (MYSQL_HOST and MYSQL_USER and MYSQL_PASSWORD):
        return None
    try:
        import mysql.connector
        return mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT
        )
    except Exception:
        return None

def get_storage_mode():
    conn = _mysql_connection()
    if conn:
        conn.close()
        return "MySQL"
    return "Local CSV demo mode (set MYSQL_HOST, MYSQL_USER and MYSQL_PASSWORD to use MySQL)"

def load_records():
    conn = _mysql_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS attendance_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(40) NOT NULL,
                    student_name VARCHAR(120) NOT NULL,
                    week INT NOT NULL,
                    classes_attended INT NOT NULL,
                    total_classes INT NOT NULL,
                    attendance_percentage FLOAT NOT NULL,
                    UNIQUE KEY unique_student_week (student_id, week)
                )
            """)
            conn.commit()
            cur.execute("SELECT student_id, student_name, week, classes_attended, total_classes, attendance_percentage FROM attendance_records ORDER BY student_id, week")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return pd.DataFrame(rows, columns=COLUMNS)
        except Exception:
            conn.close()
            raise
    if CSV_PATH.exists():
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame(columns=COLUMNS)

def save_record(row):
    conn = _mysql_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS attendance_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(40) NOT NULL,
                    student_name VARCHAR(120) NOT NULL,
                    week INT NOT NULL,
                    classes_attended INT NOT NULL,
                    total_classes INT NOT NULL,
                    attendance_percentage FLOAT NOT NULL,
                    UNIQUE KEY unique_student_week (student_id, week)
                )
            """)
            cur.execute("""
                INSERT INTO attendance_records
                (student_id, student_name, week, classes_attended, total_classes, attendance_percentage)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    student_name=VALUES(student_name),
                    classes_attended=VALUES(classes_attended),
                    total_classes=VALUES(total_classes),
                    attendance_percentage=VALUES(attendance_percentage)
            """, (row["student_id"], row["student_name"], row["week"], row["classes_attended"], row["total_classes"], row["attendance_percentage"]))
            conn.commit()
            cur.close()
            conn.close()
            return
        except Exception:
            conn.close()
            raise
    current = load_records()
    new_row = pd.DataFrame([row], columns=COLUMNS)
    current = current[~((current["student_id"].astype(str) == str(row["student_id"])) & (pd.to_numeric(current["week"], errors="coerce") == int(row["week"])))]
    combined = pd.concat([current, new_row], ignore_index=True)
    combined.to_csv(CSV_PATH, index=False)
