"""
API v1 routes
"""

from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import jsonify, request
from flask_login import current_user, login_required

from app.blueprints.api.v1 import api_bp
from app.repositories.patient_repository import PatientRepository
from app.security.rate_limit import rate_limit_api
from app.services.patient_service import PatientService

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


def jwt_required(f):
    """JWT authentication decorator"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Missing authentication token"}), 401

        try:
            from flask import current_app

            secret = current_app.config.get("JWT_SECRET_KEY")
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            # Store in request for use in route handlers
            request.current_user_id = payload["user_id"]
            request.current_username = payload["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except (jwt.InvalidTokenError, Exception) as e:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated_function


@api_bp.route("/auth/login", methods=["POST"])
def api_login():
    """API login endpoint - returns JWT token"""
    from flask import current_app

    from app.repositories.user_repository import UserRepository
    from app.services.auth_service import AuthService

    user_repo = UserRepository()
    auth_service = AuthService(user_repo)

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    success, message, user = auth_service.authenticate_user(username, password)

    if success and user:
        # Generate JWT token
        secret = current_app.config.get("JWT_SECRET_KEY")
        expiration = datetime.utcnow() + current_app.config.get(
            "JWT_EXPIRATION_DELTA", timedelta(hours=24)
        )

        token = jwt.encode(
            {
                "user_id": user.id,
                "username": user.username,
                "exp": expiration,
                "iat": datetime.utcnow(),
            },
            secret,
            algorithm="HS256",
        )

        return (
            jsonify(
                {
                    "success": True,
                    "token": token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    },
                }
            ),
            200,
        )
    else:
        return jsonify({"success": False, "error": message}), 401


@api_bp.route("/patients", methods=["GET"])
@jwt_required
def api_list_patients():
    """Get all patients (paginated)"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    patients, total = patient_service.get_patients(page, per_page)

    return (
        jsonify(
            {
                "success": True,
                "data": patients,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page,
                },
            }
        ),
        200,
    )


@api_bp.route("/patients/<patient_id>", methods=["GET"])
@jwt_required
def api_get_patient(patient_id):
    """Get patient by ID"""
    patient = patient_service.get_patient(patient_id)

    if not patient:
        return jsonify({"success": False, "error": "Patient not found"}), 404

    patient["_id"] = str(patient["_id"])
    return jsonify({"success": True, "data": patient}), 200


@api_bp.route("/patients", methods=["POST"])
@jwt_required
def api_create_patient():
    """Create new patient"""
    data = request.get_json()

    success, message, patient_id = patient_service.create_patient(
        data, request.current_username
    )

    if success:
        return (
            jsonify({"success": True, "message": message, "patient_id": patient_id}),
            201,
        )
    else:
        return jsonify({"success": False, "error": message}), 400


@api_bp.route("/patients/<patient_id>", methods=["PUT"])
@jwt_required
def api_update_patient(patient_id):
    """Update patient"""
    data = request.get_json()

    success, message = patient_service.update_patient(
        patient_id, data, request.current_username
    )

    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 400


@api_bp.route("/patients/<patient_id>", methods=["DELETE"])
@jwt_required
def api_delete_patient(patient_id):
    """Delete patient"""
    success, message = patient_service.delete_patient(
        patient_id, request.current_username
    )

    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 404


@api_bp.route("/patients/search", methods=["GET"])
@jwt_required
def api_search_patients():
    """Search patients"""
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"success": False, "error": "Search query required"}), 400

    results = patient_service.search_patients(query)
    for patient in results:
        patient["_id"] = str(patient["_id"])

    return jsonify({"success": True, "data": results, "count": len(results)}), 200


@api_bp.route("/statistics", methods=["GET"])
@jwt_required
def api_statistics():
    """Get patient statistics"""
    stats = patient_service.get_statistics()
    return jsonify({"success": True, "data": stats}), 200
