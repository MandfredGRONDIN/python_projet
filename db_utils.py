from db import get_db_connection
from werkzeug.security import generate_password_hash

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS client_movements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        client_id INT NOT NULL,
        ap_id INT NOT NULL,
        session_id INT NOT NULL,
        movement_time DATETIME NOT NULL,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (ap_id) REFERENCES wifi_access_points(id),
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

    process_and_insert_sessions()
    record_all_client_movements()

def process_and_insert_sessions():
    from insert_db import analyser_fichier_csv, insert_session_into_db  
    nom_fichier_csv = './files/log_wifi_red_hot.csv'
    sessions = analyser_fichier_csv(nom_fichier_csv)

    if sessions:
        for session in sessions:
            insert_session_into_db(session)
        print("Sessions enregistrées dans la base de données.")
    else:
        print("Aucune session trouvée dans le fichier CSV.")

def record_client_movement(client_id, ap_id, session_id, movement_time):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO client_movements (client_id, ap_id, session_id, movement_time) VALUES (%s, %s, %s, %s)",
                   (client_id, ap_id, session_id, movement_time))
    conn.commit()
    cursor.close()
    conn.close()

def record_all_client_movements():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT clients_sessions.client_id, sessions.ap_id, sessions.id, sessions.session_associated_time
    FROM clients_sessions
    JOIN sessions ON clients_sessions.session_id = sessions.id
    """)

    movements = cursor.fetchall()

    for movement in movements:
        client_id, ap_id, session_id, movement_time = movement
        record_client_movement(client_id, ap_id, session_id, movement_time)

    cursor.close()
    conn.close()

def get_ap_info(ap_id):
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

    return ap_info

def get_all_aps():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, ap_name FROM wifi_access_points")
    aps = cursor.fetchall()

    cursor.close()
    conn.close()

    return aps

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def create_user(username, password):
    hashed_password = generate_password_hash(password, method='scrypt')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()

def list_clients():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, mac_address, host_name FROM clients")
    clients = cursor.fetchall()

    cursor.close()
    conn.close()

    return clients

def get_client_info(client_id):
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

    return client_info

def get_total_aps():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM wifi_access_points")
    total_aps = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total_aps

def get_total_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clients")
    total_clients = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total_clients

def get_total_volume():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(upstream_transferred) FROM sessions")
    total_volume_upstream = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(downstream_transferred) FROM sessions")
    total_volume_downstream = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total_volume_upstream, total_volume_downstream

def get_dashboard_data():
    total_aps = get_total_aps()
    total_clients = get_total_clients()
    total_volume_upstream, total_volume_downstream = get_total_volume()
    total_volume = total_volume_upstream + total_volume_downstream
    return total_aps, total_clients, total_volume, total_volume_upstream, total_volume_downstream

def get_client_movement(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wifi_access_points.ap_name, client_movements.movement_time
        FROM client_movements
        JOIN wifi_access_points ON client_movements.ap_id = wifi_access_points.id
        WHERE client_movements.client_id = %s
        ORDER BY client_movements.movement_time ASC
    """, (client_id,))

    movements = cursor.fetchall()

    cursor.close()
    conn.close()
    return movements
