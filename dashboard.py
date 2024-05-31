from flask import render_template, redirect, url_for, session
from db_utils import get_dashboard_data

def home_utils():
    username = session.get('username')
    if username:
        return redirect(url_for('route.dashboard'))
    else:
        return redirect(url_for('route.login'))

def dashboard_utils():
    username = session.get('username')
    total_aps, total_clients, total_volume = get_dashboard_data()

    return render_template('dashboard.html', username=username, total_aps=total_aps, total_clients=total_clients, total_volume=total_volume)
