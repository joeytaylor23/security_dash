import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QComboBox, QMessageBox
)
from loguru import logger

def save_incident_log(severity, description):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="CenaVsPunk2011!",  # Change to your MySQL password
            database="security_app"
        )
        if connection.is_connected():
            cursor = connection.cursor()
            sql = "INSERT INTO incident_logs (severity, description) VALUES (%s, %s)"
            cursor.execute(sql, (severity, description))
            connection.commit()
            logger.info(f"Incident log saved: {severity} - {description}")

    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_incident_response_tab():
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Incident Response")
    layout.addWidget(label)

    severity_label = QLabel("Select Severity:")
    layout.addWidget(severity_label)

    severity_combo = QComboBox()
    severity_combo.addItems(["Low", "Medium", "High", "Critical"])
    layout.addWidget(severity_combo)

    description_label = QLabel("Incident Description:")
    layout.addWidget(description_label)

    description_text_edit = QTextEdit()
    layout.addWidget(description_text_edit)

    result_box = QTextEdit()
    result_box.setReadOnly(True)
    layout.addWidget(result_box)

    button_layout = QHBoxLayout()
    save_button = QPushButton("Save Incident")
    submit_button = QPushButton("Submit Incident")
    button_layout.addWidget(save_button)
    button_layout.addWidget(submit_button)
    layout.addLayout(button_layout)

    def save_incident():
        severity = severity_combo.currentText()
        description = description_text_edit.toPlainText().strip()

        if not description:
            QMessageBox.warning(tab, "Input Error", "Please enter an incident description.")
            return

        save_incident_log(severity, description)
        result_box.append(f"[Saved] {severity} - {description}")
        description_text_edit.clear()

    save_button.clicked.connect(save_incident)

    tab.setLayout(layout)
    return tab
