from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
import random


def get_threat_detection_tab():
    widget = QWidget()
    layout = QVBoxLayout()

    title = QLabel("Threat Detection")
    title.setStyleSheet("font-size: 18px; font-weight: bold;")

    results_box = QTextEdit()
    results_box.setReadOnly(True)

    scan_button = QPushButton("Run Threat Scan")

    def run_threat_scan():
        results_box.clear()
        results_box.append("🔍 Scanning for threats...")

        # Simulated threat scan (replace with real logic later)
        fake_threats = [
            "✔️ No threats found.",
            "⚠️ Suspicious file: C:/Users/Username/Documents/malicious.exe",
            "⚠️ Anomaly detected in network traffic (port 8080).",
            "✔️ System registry is clean.",
            "⚠️ Elevated privileges attempt detected.",
        ]

        # Randomly pick 2–3 results to simulate scanning
        threats_found = random.sample(fake_threats, k=random.randint(2, 4))
        for line in threats_found:
            results_box.append(line)

    scan_button.clicked.connect(run_threat_scan)

    layout.addWidget(title)
    layout.addWidget(results_box)
    layout.addWidget(scan_button)

    widget.setLayout(layout)
    return widget
