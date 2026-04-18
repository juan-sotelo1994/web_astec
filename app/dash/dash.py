from flask import render_template
from . import dashboard_bp

@dashboard_bp.route('/dashboard')
def dash_view():
    return render_template('dashboard.html')
