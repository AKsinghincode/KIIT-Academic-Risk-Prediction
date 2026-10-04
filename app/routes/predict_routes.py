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
            'attendance': request.form.get('attendance', 0),
            'midterm': request.form.get('midterm', 0),
            'assignment': request.form.get('assignment', 0),
            'quiz': request.form.get('quiz', 0),
            'study_hours': request.form.get('study_hours', 0),
            'backlogs': request.form.get('backlogs', 0)
        }
        
        result = PredictionService.predict_risk(data)
        
        # Save record to SQLite database
        try:
            db = get_db()
            db.execute(
                'INSERT INTO student_risk_records (attendance, midterm, risk_level, confidence)'
                ' VALUES (?, ?, ?, ?)',
                (float(data['attendance']), float(data['midterm']), result['risk_level'], result['confidence'])
            )
            db.commit()
        except Exception as e:
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
    if file and file.filename.endswith('.csv'):
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        db = get_db()
        for row in csv_input:
            prediction = PredictionService.predict_risk(row)
            res_dict = {
                'roll_number': row.get('roll_number', 'N/A'),
                'name': row.get('name', 'N/A'),
                'risk_level': prediction['risk_level'],
                'confidence': prediction['confidence'],
                'key_factors': prediction['key_factors']
            }
            results.append(res_dict)

            # Persist batch record to database
            try:
                db.execute(
                    'INSERT INTO student_risk_records (attendance, midterm, risk_level, confidence)'
                    ' VALUES (?, ?, ?, ?)',
                    (float(row.get('attendance', 0)), float(row.get('midterm', 0)), prediction['risk_level'], prediction['confidence'])
                )
            except Exception:
                pass
        
        db.commit()

    return render_template('predict/batch_result.html', results=results)