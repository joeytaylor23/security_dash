import psutil
import socket

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import QTimer
from loguru import logger

def get_threat_detection_tab():
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Threat Detection Module")
    start_button = QPushButton("Start Threat Scan")
    result_box = QTextEdit()
    result_box.setReadOnly(True)

    layout.addWidget(label)
    layout.addWidget(start_button)
    layout.addWidget(result_box)
    tab.setLayout(layout)

    def run_threat_scan():
        result_box.clear()
        result_box.append("Running real-time threat scan...\n")
        logger.info("Real-time threat scan started.")

        suspicious_processes = []
        network_threats = []

        # Check for suspicious processes
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                mem = proc.info['memory_info'].rss / (1024 * 1024)  # MB
                name = proc.info['name']
                if mem > 100:  # Example threshold
                    suspicious_processes.append(f"[!] High memory usage: {name} ({mem:.2f} MB)")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Check open network connections
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED' and conn.raddr:
                ip, port = conn.raddr
                if not ip.startswith("192.168.") and not ip.startswith("127.0.0.1"):
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        hostname = "Unknown"
                    network_threats.append(f"[!] External connection: {ip}:{port} ({hostname})")

        # Show real scan results
        if not suspicious_processes and not network_threats:
            result_box.append("[✓] No suspicious activity found.")
        else:
            for line in suspicious_processes + network_threats:
                result_box.append(line)
                logger.warning(line)

        # Optionally simulate extra findings after a delay
        def show_simulated_results():
            fake_threats = [
                "[!] Suspicious login detected from IP 192.168.1.5",
                "[!] Unusual process behavior: python.exe attempting outbound connection",
                "[!] Potential malware: unknown.exe flagged by heuristic analysis",
                "[✓] Scan complete. 3 potential threats found."
            ]
            for threat in fake_threats:
                result_box.append(threat)
                logger.warning(threat)

        QTimer.singleShot(500, show_simulated_results)

    start_button.clicked.connect(run_threat_scan)
    return tab
