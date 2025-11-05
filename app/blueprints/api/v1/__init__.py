"""
API v1 blueprint
"""

from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

from app.blueprints.api.v1 import routes  # noqa: F401,E402
