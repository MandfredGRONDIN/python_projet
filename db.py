import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'python'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn
