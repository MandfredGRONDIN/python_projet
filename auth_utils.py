from flask import request, redirect, url_for, session
from flask_jwt_extended import create_access_token, set_access_cookies
from werkzeug.security import check_password_hash
from db_utils import get_user_by_username, create_user

def login_user():
    username = request.form.get('username')
    password = request.form.get('password')
    user = get_user_by_username(username)
    if user and check_password_hash(user[2], password):
        access_token = create_access_token(identity=username)
        session['username'] = username
        session['access_token'] = access_token
        response = redirect(url_for('route.dashboard'))
        set_access_cookies(response, access_token) 
        return response
    else:
        return redirect(url_for('route.login'))

def register_user():
    username = request.form.get('username')
    password = request.form.get('password')
    create_user(username, password)
    return redirect(url_for('route.login'))
