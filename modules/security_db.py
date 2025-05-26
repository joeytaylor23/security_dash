import mysql.connector
from mysql.connector import Error

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="CenaVsPunk2011!",
        database="security_app"
    )

def save_incident_log(incident_text):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO incident_logs (incident) VALUES (%s)"
        cursor.execute(query, (incident_text,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"[DB ERROR] {e}")
        return False
