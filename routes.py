from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from flask_jwt_extended import jwt_required
from auth_utils import login_user, register_user
from client_utils import list_clients_utils, client_utils
from aps_utils import wifi_ap_utils, list_aps_utils
from dashboard import dashboard_utils, home_utils
from db_utils import init_db, get_client_movement

route_blueprint = Blueprint('route', __name__)

def initialize_database():
    try:
        init_db()
        return jsonify({"msg": "Database initialized"}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

@route_blueprint.before_request
def add_jwt_token_to_headers():
    access_token = session.get('access_token')
    if access_token and 'Authorization' not in request.headers:
        new_headers = request.headers.to_wsgi_list()
        new_headers.append(('Authorization', f"Bearer {access_token}"))
        request.environ['HTTP_AUTHORIZATION'] = f"Bearer {access_token}"

@route_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return login_user()
    return render_template('login.html')

@route_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return register_user()
    return render_template('register.html')

@route_blueprint.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  
    session.pop('access_token', None)
    return redirect(url_for('route.login'))

@route_blueprint.route('/')
def home():
    return home_utils()

@route_blueprint.route('/dashboard')
@jwt_required()
def dashboard():
    return dashboard_utils()

@route_blueprint.route('/wifi_ap/<int:ap_id>')
@jwt_required()
def wifi_ap(ap_id):
    return wifi_ap_utils(ap_id)

@route_blueprint.route('/client/<int:client_id>')
@jwt_required()
def client(client_id):
    return client_utils(client_id)

@route_blueprint.route('/list_aps')
@jwt_required()
def list_aps():
    return list_aps_utils()

@route_blueprint.route('/list_clients')
@jwt_required()
def list_clients():
    return list_clients_utils()

@route_blueprint.route('/client/<int:client_id>/movement_history')
@jwt_required()
def client_movement_history(client_id):
    movements = get_client_movement(client_id)
    return render_template('client_movement_history.html', movements=movements)