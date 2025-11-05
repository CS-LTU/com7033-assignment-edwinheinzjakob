"""
Root routes
"""
def register_routes(app):
    """Register root-level routes"""
    from flask import render_template, redirect, url_for
    from flask_login import current_user
    
    @app.route('/')
    def index():
        """Home page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('index.html')

