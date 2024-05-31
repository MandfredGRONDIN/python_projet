from db_utils import get_db_connection

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

    process_and_insert_sessions()

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
