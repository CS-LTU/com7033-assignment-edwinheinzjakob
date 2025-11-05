"""
Patient management routes
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.blueprints.patients import patients_bp
from app.repositories.patient_repository import PatientRepository
from app.services.patient_service import PatientService
from app.security.rate_limit import (
    rate_limit_crud,
    rate_limit_search,
    rate_limit_import,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd

# Initialize services
patient_repo = PatientRepository()
patient_service = PatientService(patient_repo)

# Limiter will be initialized in app factory
limiter = None


def init_limiter(app):
    """Initialize limiter for this blueprint"""
    global limiter
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(app=app, key_func=get_remote_address)


@patients_bp.route("/")
@login_required
def list_patients():
    """View all patients"""
    page = request.args.get("page", 1, type=int)
    per_page = 20

    patients, total = patient_service.get_patients(page, per_page)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "patients.html", patients=patients, page=page, total_pages=total_pages
    )


@patients_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_patient():
    """Add new patient"""
    if request.method == "POST":
        patient_data = {
            "id": int(request.form.get("id")),
            "gender": request.form.get("gender"),
            "age": float(request.form.get("age")),
            "hypertension": int(request.form.get("hypertension")),
            "heart_disease": int(request.form.get("heart_disease")),
            "ever_married": request.form.get("ever_married"),
            "work_type": request.form.get("work_type"),
            "Residence_type": request.form.get("Residence_type"),
            "avg_glucose_level": float(request.form.get("avg_glucose_level")),
            "bmi": float(request.form.get("bmi")),
            "smoking_status": request.form.get("smoking_status"),
            "stroke": int(request.form.get("stroke")),
        }

        success, message, patient_id = patient_service.create_patient(
            patient_data, current_user.username
        )

        if success:
            flash(message, "success")
            return redirect(url_for("patients.list_patients"))
        else:
            flash(message, "danger")
            return redirect(url_for("patients.add_patient"))

    return render_template("add_patient.html")


@patients_bp.route("/edit/<patient_id>", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    """Edit existing patient"""
    if request.method == "POST":
        update_data = {
            "gender": request.form.get("gender"),
            "age": float(request.form.get("age")),
            "hypertension": int(request.form.get("hypertension")),
            "heart_disease": int(request.form.get("heart_disease")),
            "ever_married": request.form.get("ever_married"),
            "work_type": request.form.get("work_type"),
            "Residence_type": request.form.get("Residence_type"),
            "avg_glucose_level": float(request.form.get("avg_glucose_level")),
            "bmi": float(request.form.get("bmi")),
            "smoking_status": request.form.get("smoking_status"),
            "stroke": int(request.form.get("stroke")),
        }

        success, message = patient_service.update_patient(
            patient_id, update_data, current_user.username
        )

        if success:
            flash(message, "success")
            return redirect(url_for("patients.list_patients"))
        else:
            flash(message, "danger")
            return redirect(url_for("patients.edit_patient", patient_id=patient_id))

    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("patients.list_patients"))

    patient["_id"] = str(patient["_id"])
    return render_template("edit_patient.html", patient=patient)


@patients_bp.route("/delete/<patient_id>", methods=["POST"])
@login_required
def delete_patient(patient_id):
    """Delete patient"""
    success, message = patient_service.delete_patient(patient_id, current_user.username)

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for("patients.list_patients"))


@patients_bp.route("/view/<patient_id>")
@login_required
def view_patient(patient_id):
    """View patient details"""
    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("patients.list_patients"))

    patient["_id"] = str(patient["_id"])
    return render_template("view_patient.html", patient=patient)


@patients_bp.route("/search")
@login_required
def search():
    """Search patients"""
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("patients.list_patients"))

    results = patient_service.search_patients(query)
    for patient in results:
        patient["_id"] = str(patient["_id"])

    return render_template("search_results.html", patients=results, query=query)


@patients_bp.route("/import", methods=["GET", "POST"])
@login_required
def import_data():
    """Import CSV data into MongoDB"""
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected.", "danger")
            return redirect(url_for("patients.import_data"))

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected.", "danger")
            return redirect(url_for("patients.import_data"))

        if not file.filename.endswith(".csv"):
            flash("Only CSV files are allowed.", "danger")
            return redirect(url_for("patients.import_data"))

        try:
            # Read CSV
            df = pd.read_csv(file)

            # Convert to dict and import
            records = df.to_dict("records")
            success, message, count = patient_service.import_patients(
                records, current_user.username
            )

            if success:
                flash(message, "success")
                return redirect(url_for("patients.list_patients"))
            else:
                flash(message, "danger")
                return redirect(url_for("patients.import_data"))
        except Exception as e:
            flash(f"Error importing data: {str(e)}", "danger")
            return redirect(url_for("patients.import_data"))

    return render_template("import_data.html")
