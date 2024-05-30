import mysql.connector
import csv
from datetime import datetime

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'python'
}

class Session:
    def __init__(self, associated_time, duration, mac_address, host_name, device, os_type, upstream_transferred, downstream_transferred, connected_ap_name):
        self.associated_time = associated_time
        self.duration = duration
        self.mac_address = mac_address
        self.host_name = host_name
        self.device = device
        self.os_type = os_type
        self.upstream_transferred = upstream_transferred
        self.downstream_transferred = downstream_transferred
        self.connected_ap_name = connected_ap_name
    def __str__(self):
        return f"Associated Time: {self.associated_time}, Duration: {self.duration}, MAC Address: {self.mac_address}, Host Name: {self.host_name}, Device: {self.device}, OS Type: {self.os_type}, Upstream Transferred: {self.upstream_transferred}, Downstream Transferred: {self.downstream_transferred}, Connected AP Name: {self.connected_ap_name}"

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

def insert_session_into_db(session):
    cursor = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        ap_id_query = "SELECT id FROM wifi_access_points WHERE ap_name = %s"
        cursor.execute(ap_id_query, (session.connected_ap_name,))
        ap_id_row = cursor.fetchone()

        if ap_id_row:
            ap_id = ap_id_row[0]
        else:
            insert_ap_query = "INSERT INTO wifi_access_points (ap_name) VALUES (%s)"
            cursor.execute(insert_ap_query, (session.connected_ap_name,))
            ap_id = cursor.lastrowid

        session_query = """
            INSERT INTO sessions (session_associated_time, session_duration, upstream_transferred, downstream_transferred, ap_id) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(session_query, (session.associated_time, session.duration, session.upstream_transferred, session.downstream_transferred, ap_id))
        session_id = cursor.lastrowid

        client_query = """
            INSERT INTO clients (mac_address, host_name, device, os_type) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id)
        """
        cursor.execute(client_query, (session.mac_address, session.host_name, session.device, session.os_type))
        client_id = cursor.lastrowid

        client_session_query = """
            INSERT INTO clients_sessions (client_id, session_id) 
            VALUES (%s, %s)
        """
        cursor.execute(client_session_query, (client_id, session_id))

        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erreur lors de l'insertion de la session dans la base de données : {err}")
    finally:
        if cursor:  
            cursor.close()
        if conn:  
            conn.close()


def analyser_fichier_csv(nom_fichier):
    sessions = []

    try:
        with open(nom_fichier, 'r', encoding='utf-8-sig') as fichier:
            csv_reader = csv.DictReader(fichier, delimiter=';')
            for row in csv_reader:
                associated_time = datetime.strptime(row['Session Associated Time'], '%d/%m/%Y %H:%M')
                duration = int(row['Session Duration'].replace(' ', '').replace(',', '').replace('.', ''))  
                mac_address = row['Client MAC Address']
                host_name = row['Host Name']
                device = row['Device']
                os_type = row['OS Type']
                upstream_transferred = int(row['Upstream Transferred (Bytes)'].replace(' ', '').replace(',', '').replace('.', ''))  
                downstream_transferred = int(row['Downstream Transferred (Bytes)'].replace(' ', '').replace(',', '').replace('.', ''))  
                connected_ap_name = row['Connected AP Name']

                session = Session(associated_time, duration, mac_address, host_name, device, os_type, upstream_transferred, downstream_transferred, connected_ap_name)
                sessions.append(session)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {nom_fichier} n'a pas été trouvé.")
    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier CSV : {e}")

    return sessions


nom_fichier_csv = './files/log_wifi_red_hot.csv'
sessions = analyser_fichier_csv(nom_fichier_csv)

if sessions:
    for session in sessions:
        #print(session)
        insert_session_into_db(session)
    print("Sessions enregistrées dans la base de données.")
