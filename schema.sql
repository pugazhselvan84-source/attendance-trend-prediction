CREATE DATABASE IF NOT EXISTS attendance_trend_prediction;
USE attendance_trend_prediction;

CREATE TABLE IF NOT EXISTS attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(40) NOT NULL,
    student_name VARCHAR(120) NOT NULL,
    week INT NOT NULL,
    classes_attended INT NOT NULL,
    total_classes INT NOT NULL,
    attendance_percentage FLOAT NOT NULL,
    UNIQUE KEY unique_student_week (student_id, week)
);
