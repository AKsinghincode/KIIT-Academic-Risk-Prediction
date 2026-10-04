import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for
from app.services.predict_service import PredictionService
from app.database import get_db

predict_bp = Blueprint('predict', __name__)

# Add this route so visiting the main site URL doesn't show 404
@predict_bp.route('/')
def home():
    return redirect(url_for('predict.single_predict'))

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
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
        csv_input = csv.DictReader(stream)
        
        db = get_db()
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
            cleaned_row = {str(k).strip(): str(v).strip() for k, v in row.items() if k is not None}
            
            try:
                feature_data = {
                    'attendance': float(cleaned_row.get('attendance', 0) or 0),
                    'midterm': float(cleaned_row.get('midterm', 0) or 0),
                    'assignment': float(cleaned_row.get('assignment', 0) or 0),
                    'quiz': float(cleaned_row.get('quiz', 0) or 0),
                    'study_hours': float(cleaned_row.get('study_hours', 0) or 0),
                    'backlogs': float(cleaned_row.get('backlogs', 0) or 0)
                }
                prediction = PredictionService.predict_risk(feature_data)
            except Exception:
                prediction = {'risk_level': 'Medium Risk', 'confidence': 50.0, 'key_factors': []}

            res_dict = {
                'roll_number': cleaned_row.get('roll_number', cleaned_row.get('roll', 'N/A')),
                'name': cleaned_row.get('name', 'N/A'),
                'attendance': float(cleaned_row.get('attendance', 0) or 0),
                'midterm': float(cleaned_row.get('midterm', 0) or 0),
                'risk_level': prediction.get('risk_level', 'Medium Risk'),
                'confidence': prediction.get('confidence', 50.0),
                'key_factors': prediction.get('key_factors', [])
            }
            results.append(res_dict)

            try:
                db.execute(
                    'INSERT INTO student_risk_records (attendance, midterm, risk_level, confidence)'
                    ' VALUES (?, ?, ?, ?)',
                    (res_dict['attendance'], res_dict['midterm'], res_dict['risk_level'], res_dict['confidence'])
                )
            except Exception:
                pass
        
        try:
            db.commit()
        except Exception:
            pass

    return render_template('predict/batch_result.html', results=results)