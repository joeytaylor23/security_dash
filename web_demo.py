from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('incidents.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    conn = get_db_connection()
    incidents = conn.execute('SELECT * FROM incidents ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify([dict(incident) for incident in incidents])

@app.route('/api/incidents', methods=['POST'])
def create_incident():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO incidents (subject, severity, description, timestamp, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['subject'],
        data['severity'],
        data['description'],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "New"
    ))
    
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True) 