"""
Dashboard routes
"""
from flask import render_template
from flask_login import login_required
from app.blueprints.dashboard import dashboard_bp
from app.repositories.patient_repository import PatientRepository

patient_repo = PatientRepository()

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard"""
    stats = patient_repo.get_statistics()
    
    return render_template('dashboard.html',
                         total_patients=stats.get('total_patients', 0),
                         stroke_patients=stats.get('stroke_patients', 0),
                         male_count=stats.get('male_count', 0),
                         female_count=stats.get('female_count', 0),
                         average_age=stats.get('average_age', 0))

