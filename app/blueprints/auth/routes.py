"""
Authentication routes
"""
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.security.validation import sanitize_input

# Initialize services
user_repo = UserRepository()
auth_service = AuthService(user_repo)

# Limiter will be initialized in app factory
limiter = None

def init_limiter(app):
    """Initialize limiter for this blueprint"""
    global limiter
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(app=app, key_func=get_remote_address)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', '').strip())
        email = sanitize_input(request.form.get('email', '').strip())
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Basic validation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Register user
        success, message, user_id = auth_service.register_user(username, email, password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', '').strip())
        password = request.form.get('password', '')
        
        # Authenticate user
        success, message, user = auth_service.authenticate_user(username, password)
        
        if success and user:
            login_user(user, remember=True)
            flash(message, 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash(message, 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    # Log action
    user_repo.log_action(
        current_user.id,
        'USER_LOGOUT',
        f'User {current_user.username} logged out',
        request.remote_addr
    )
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

