import joblib
import os

class PredictionService:
    @staticmethod
    def predict_risk(data):
        try:
            attendance = float(data.get('attendance', 0))
            midterm = float(data.get('midterm', 0))
        except (ValueError, TypeError):
            attendance, midterm = 0.0, 0.0

        if attendance < 60 or midterm < 40:
            risk_level = 'High'
            confidence = 0.88
            factors = 'Low Attendance, Poor Midterm Performance'
        elif attendance < 75 or midterm < 60:
            risk_level = 'Medium'
            confidence = 0.72
            factors = 'Borderline Attendance or Assessment Marks'
        else:
            risk_level = 'Low'
            confidence = 0.95
            factors = 'Good Attendance and Exam Scores'

        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'key_factors': factors
        }