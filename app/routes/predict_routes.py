import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for
from app.services.predict_service import PredictionService
from app.database import get_db

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['GET', 'POST'])
def single_predict():
    if request.method == 'POST':
        data = {
            'attendance': float(request.form.get('attendance', 0) or 0),
            'midterm': float(request.form.get('midterm', 0) or 0),
            'assignment': float(request.form.get('assignment', 0) or 0),
            'quiz': float(request.form.get('quiz', 0) or 0),
            'study_hours': float(request.form.get('study_hours', 0) or 0),
            'backlogs': float(request.form.get('backlogs', 0) or 0)
        }
        
        result = PredictionService.predict_risk(data)
        
        # Save record to SQLite database
        try:
            db = get_db()
            db.execute('''
                CREATE TABLE IF NOT EXISTS student_risk_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attendance REAL,
                    midterm REAL,
                    risk_level TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.execute(
                'INSERT INTO student_risk_records (attendance, midterm, risk_level, confidence)'
                ' VALUES (?, ?, ?, ?)',
                (data['attendance'], data['midterm'], result['risk_level'], result['confidence'])
            )
            db.commit()
        except Exception:
            pass

        return render_template('predict/result.html', result=result)
        
    return render_template('predict/single.html')


@predict_bp.route('/predict/batch', methods=['POST'])
def batch_predict():
    if 'file' not in request.files:
        return redirect(url_for('predict.single_predict'))
        
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('predict.single_predict'))

    results = []
    if file and (file.filename.endswith('.csv') or file.filename.endswith('.txt')):
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        db = get_db()
        # Ensure database table exists
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS student_risk_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attendance REAL,
                    midterm REAL,
                    risk_level TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        except Exception:
            pass
            
        for row in csv_input:
            # Parse row data into float numbers for ML prediction service
            feature_data = {
                'attendance': float(row.get('attendance', 0) or 0),
                'midterm': float(row.get('midterm', 0) or 0),
                'assignment': float(row.get('assignment', 0) or 0),
                'quiz': float(row.get('quiz', 0) or 0),
                'study_hours': float(row.get('study_hours', 0) or 0),
                'backlogs': float(row.get('backlogs', 0) or 0)
            }
            
            prediction = PredictionService.predict_risk(feature_data)
            res_dict = {
                'roll_number': row.get('roll_number', 'N/A'),
                'name': row.get('name', 'N/A'),
                'risk_level': prediction['risk_level'],
                'confidence': prediction['confidence'],
                'key_factors': prediction.get('key_factors', [])
            }
            results.append(res_dict)

            # Persist batch record to database
            try:
                db.execute(
                    'INSERT INTO student_risk_records (attendance, midterm, risk_level, confidence)'
                    ' VALUES (?, ?, ?, ?)',
                    (feature_data['attendance'], feature_data['midterm'], prediction['risk_level'], prediction['confidence'])
                )
            except Exception:
                pass
        
        try:
            db.commit()
        except Exception:
            pass

    return render_template('predict/batch_result.html', results=results)