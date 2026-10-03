import csv
import io
from flask import Blueprint, render_template, Response

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    return render_template('dashboard/index.html')

@dashboard_bp.route('/dashboard/export-high-risk')
def export_high_risk():
    # Sample high risk records retrieved for export
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Roll Number', 'Student Name', 'Risk Level', 'Key Risk Factors'])
    
    # Sample Data (or load directly from database queries)
    writer.writerow(['PAS077BCT003', 'Anmol limbu', 'High', 'Low Attendance, High Backlogs'])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=high_risk_students.csv"}
    )