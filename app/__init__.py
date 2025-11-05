"""
Secure Stroke Prediction Dataset Management System
Main application factory
"""

import logging

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from pythonjsonlogger import jsonlogger
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app.repositories.user_repository import UserRepository
from app.security.encryption import EncryptionService, init_encryption_service
from app.utils.logging_config import setup_logging
from config import config

# Initialize extensions
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()
talisman = Talisman()


def create_app(config_name="development"):
    """Application factory pattern"""
    import os

    # Get the root directory (parent of app directory)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(root_dir, "templates")
    static_dir = os.path.join(root_dir, "static")

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config[config_name])

    # Initialize extensions
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # Initialize Talisman with security headers
    csp_policy = app.config.get("SECURITY_HEADERS", {}).get(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;",
    )

    talisman.init_app(
        app,
        force_https=app.config.get("SESSION_COOKIE_SECURE", False),
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        content_security_policy=csp_policy,
    )

    # Initialize rate limiting
    limiter.init_app(app)

    # Initialize limiter in blueprints
    from app.blueprints.auth.routes import init_limiter as init_auth_limiter

    init_auth_limiter(app)
    from app.blueprints.patients.routes import init_limiter as init_patients_limiter

    init_patients_limiter(app)
    from app.blueprints.api.v1.routes import init_limiter as init_api_limiter

    init_api_limiter(app)

    # Setup logging
    setup_logging(app)

    # Initialize encryption service
    encryption_key = app.config.get("ENCRYPTION_KEY")
    if encryption_key:
        init_encryption_service(encryption_key)

    # Initialize Sentry if configured
    sentry_dsn = app.config.get("SENTRY_DSN")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=config_name,
        )

    # Initialize repositories
    user_repo = UserRepository()

    # Setup login manager user loader
    @login_manager.user_loader
    def load_user(user_id):
        return user_repo.get_user_by_id(int(user_id))

    # Make csrf_token available in templates
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf

        return dict(csrf_token=generate_csrf)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.patients import patients_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(patients_bp, url_prefix="/patients")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    # Register API blueprint (using plain Flask routes, not Flask-Smorest)
    from app.blueprints.api.v1 import api_bp

    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # Register root routes
    from app.routes import register_routes

    register_routes(app)

    # Register error handlers
    from app.errors import register_error_handlers

    register_error_handlers(app)

    return app
