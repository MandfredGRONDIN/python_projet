from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
import mysql.connector
from db import init_db

auth_blueprint = Blueprint('auth', __name__)

def initialize_database():
    try:
        init_db()
        return jsonify({"msg": "Database initialized"}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user[2], password):
            access_token = create_access_token(identity=username)
            flash('Login successful', 'success')
            session['username'] = username
            return redirect(url_for('auth.home'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='scrypt')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO USERS (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Registration successful', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  
    flash('Successfully logged out', 'success')  
    return redirect(url_for('auth.login')) 


@auth_blueprint.route('/home')
def home():
    username = session.get('username') 
    if username:
        return render_template('index.html', username=username)
    else:
        flash('You need to login first', 'error')
        return redirect(url_for('auth.login'))
