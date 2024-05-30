from flask import Flask
from flask_jwt_extended import JWTManager
from auth import auth_blueprint, initialize_database

app = Flask(__name__)
app.secret_key = 'test'
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

app.register_blueprint(auth_blueprint)

@app.route('/init_db', methods=['GET'])
def init_db_route():
    return initialize_database()

if __name__ == '__main__':
    app.run(debug=True, port=5005)
