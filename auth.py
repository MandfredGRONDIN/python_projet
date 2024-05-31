from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import create_access_token, jwt_required, set_access_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from db_utils import get_db_connection 

auth_blueprint = Blueprint('auth', __name__)

def initialize_database():
    try:
        init_db()
        return jsonify({"msg": "Database initialized"}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

@auth_blueprint.before_request
def add_jwt_token_to_headers():
    access_token = session.get('access_token')
    if access_token and 'Authorization' not in request.headers:
        new_headers = request.headers.to_wsgi_list()
        new_headers.append(('Authorization', f"Bearer {access_token}"))
        request.environ['HTTP_AUTHORIZATION'] = f"Bearer {access_token}"

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
            session['username'] = username
            session['access_token'] = access_token
            flash('Login successful', 'success')
            response = redirect(url_for('auth.dashboard'))
            set_access_cookies(response, access_token) 
            return response
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
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Registration successful', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  
    session.pop('access_token', None)
    flash('Successfully logged out', 'success')  
    return redirect(url_for('auth.login'))

@auth_blueprint.route('/')
def home():
    username = session.get('username')
    if username:
        return redirect(url_for('auth.dashboard'))
    else:
        flash('You need to login first', 'error')
        return redirect(url_for('auth.login'))

@auth_blueprint.route('/dashboard')
@jwt_required()
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM wifi_access_points")
    total_aps = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM clients")
    total_clients = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(upstream_transferred + downstream_transferred) FROM sessions")
    total_volume = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template('dashboard.html', total_aps=total_aps, total_clients=total_clients, total_volume=total_volume)

@auth_blueprint.route('/wifi_ap/<int:ap_id>')
@jwt_required()
def wifi_ap(ap_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            ap_name, 
            SUM(upstream_transferred) as total_upstream, 
            SUM(downstream_transferred) as total_downstream 
        FROM wifi_access_points 
        JOIN sessions ON wifi_access_points.id = sessions.ap_id 
        WHERE wifi_access_points.id = %s
        GROUP BY ap_name
    """, (ap_id,))
    ap_info = cursor.fetchone()

    cursor.close()
    conn.close()

    if ap_info:
        return render_template('wifi_ap.html', ap_info=ap_info)
    else:
        flash('Borne WiFi introuvable', 'error')
        return redirect(url_for('auth.dashboard'))

@auth_blueprint.route('/client/<int:client_id>')
@jwt_required()
def client(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            clients.mac_address, 
            clients.host_name, 
            clients.device, 
            clients.os_type, 
            SUM(sessions.session_duration) as total_duration, 
            GROUP_CONCAT(DISTINCT wifi_access_points.ap_name SEPARATOR ', ') as connected_aps, 
            SUM(sessions.upstream_transferred) as total_upstream, 
            SUM(sessions.downstream_transferred) as total_downstream 
        FROM clients 
        JOIN clients_sessions ON clients.id = clients_sessions.client_id 
        JOIN sessions ON clients_sessions.session_id = sessions.id 
        JOIN wifi_access_points ON sessions.ap_id = wifi_access_points.id 
        WHERE clients.id = %s
        GROUP BY clients.id
    """, (client_id,))
    client_info = cursor.fetchone()

    cursor.close()
    conn.close()

    if client_info:
        return render_template('client.html', client_info=client_info)
    else:
        flash('Client introuvable', 'error')
        return redirect(url_for('auth.dashboard'))

@auth_blueprint.route('/list_aps')
@jwt_required()
def list_aps():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, ap_name FROM wifi_access_points")
    aps = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('list_aps.html', aps=aps)

@auth_blueprint.route('/list_clients')
@jwt_required()
def list_clients():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, mac_address, host_name FROM clients")
    clients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('list_clients.html', clients=clients)