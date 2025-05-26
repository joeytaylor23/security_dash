from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from loguru import logger
import mysql.connector
from mysql.connector import Error

def get_incident_log_tab():
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Incident Log Viewer")
    layout.addWidget(label)

    result_box = QTextEdit()
    result_box.setReadOnly(True)
    layout.addWidget(result_box)

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="CenaVsPunk2011!",
            database="security_app"
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT id, severity, description, timestamp FROM incident_logs ORDER BY timestamp DESC")
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    id, severity, description, timestamp = row
                    result_box.append(f"[{timestamp}] {severity} - {description}")
            else:
                result_box.append("No incidents logged yet.")

    except Error as e:
        logger.error(f"Database error: {e}")
        result_box.append(f"[!] Failed to load incidents: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

    tab.setLayout(layout)
    return tab
