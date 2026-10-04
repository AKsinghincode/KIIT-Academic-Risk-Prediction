from flask import Blueprint, render_template
from app.database import get_db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    records = []
    total_students = 0
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0

    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_risk_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attendance REAL,
                midterm REAL,
                risk_level TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('SELECT * FROM student_risk_records ORDER BY id DESC')
        records = cursor.fetchall()
        
        total_students = len(records)

        # Count directly using SQL or direct dict key access
        for row in records:
            # Convert row to dictionary safely and strip any extra whitespace
            row_dict = dict(row)
            level = str(row_dict.get('risk_level', '')).strip()

            if level == 'High Risk':
                high_risk_count += 1
            elif level == 'Medium Risk':
                medium_risk_count += 1
            elif level == 'Low Risk':
                low_risk_count += 1

    except Exception:
        pass

    return render_template(
        'dashboard/index.html',
        records=records,
        total_students=total_students,
        high_risk_count=high_risk_count,
        medium_risk_count=medium_risk_count,
        low_risk_count=low_risk_count
    )