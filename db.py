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

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        mac_address VARCHAR(17) NOT NULL UNIQUE,
        host_name VARCHAR(100) NOT NULL,
        device VARCHAR(50) NOT NULL,
        os_type VARCHAR(50) NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wifi_access_points (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ap_name VARCHAR(100) NOT NULL UNIQUE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_associated_time DATETIME NOT NULL,
        session_duration INT NOT NULL,
        upstream_transferred BIGINT NOT NULL,
        downstream_transferred BIGINT NOT NULL,
        ap_id INT NOT NULL,
        FOREIGN KEY (ap_id) REFERENCES wifi_access_points(id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients_sessions (
        client_id INT NOT NULL,
        session_id INT NOT NULL,
        PRIMARY KEY (client_id, session_id),
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()
