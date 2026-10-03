import os
import sqlite3
from app.database import get_db

class AcademicModel:
    @staticmethod
    def get_all_students_with_risk():
        db = get_db()
        try:
            cursor = db.execute('''
                SELECT s.roll_number, s.first_name, s.last_name, c.course_code,
                       ar.attendance_percentage, ar.midterm_score,
                       p.risk_level, p.confidence_score, p.key_risk_factors
                FROM student_profiles s
                JOIN academic_records ar ON s.student_id = ar.student_id
                JOIN courses c ON ar.course_id = c.course_id
                JOIN predictions p ON ar.record_id = p.record_id
                ORDER BY p.prediction_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            return []

    @staticmethod
    def save_academic_record_and_prediction(student_id, course_id, metrics, risk_result):
        db = get_db()
        # Ensure tables exist
        db.executescript('''
            CREATE TABLE IF NOT EXISTS student_profiles (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number TEXT,
                first_name TEXT,
                last_name TEXT
            );
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT
            );
            CREATE TABLE IF NOT EXISTS academic_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                course_id INTEGER,
                attendance_percentage REAL,
                midterm_score REAL
            );
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER,
                risk_level TEXT,
                confidence_score REAL,
                key_risk_factors TEXT,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        cursor = db.cursor()
        cursor.execute('INSERT INTO academic_records (student_id, course_id, attendance_percentage, midterm_score) VALUES (?, ?, ?, ?)',
                       (student_id, course_id, metrics.get('attendance', 0), metrics.get('midterm', 0)))
        record_id = cursor.lastrowid
        cursor.execute('INSERT INTO predictions (record_id, risk_level, confidence_score, key_risk_factors) VALUES (?, ?, ?, ?)',
                       (record_id, risk_result.get('risk_level', 'Medium'), risk_result.get('confidence', 0.5), risk_result.get('key_factors', 'N/A')))
        db.commit()