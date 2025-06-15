import psutil
import socket
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QProgressBar)
from PyQt5.QtCore import QTimer, Qt
from loguru import logger
from .gui_components import (StyledLabel, StyledButton, StyledGroupBox, 
                           DataCard, COLORS)

class ThreatDetectionModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.is_scanning = False
        
    def setup_ui(self):
        layout = QVBoxLayout()

        # Header
        header = StyledLabel("Threat Detection Center", is_title=True)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Stats section
        stats_layout = QHBoxLayout()
        
        self.threats_card = DataCard("Threats Detected", "0")
        self.processes_card = DataCard("Processes Scanned", "0")
        self.connections_card = DataCard("Network Connections", "0")
        self.last_scan_card = DataCard("Last Scan", "Never")
        
        for card in [self.threats_card, self.processes_card, 
                    self.connections_card, self.last_scan_card]:
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Scan progress section
        scan_group = StyledGroupBox("Scan Progress")
        scan_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333333;
                border-radius: 5px;
                text-align: center;
                background-color: #1E1E1E;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setTextVisible(True)
        scan_layout.addWidget(self.progress_bar)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        self.start_button = StyledButton("Start Threat Scan")
        self.start_button.clicked.connect(self.toggle_scan)
        buttons_layout.addWidget(self.start_button)
        
        scan_layout.addLayout(buttons_layout)
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)
        
        # Results section
        results_group = StyledGroupBox("Scan Results")
        results_layout = QVBoxLayout()
        
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        results_layout.addWidget(self.result_box)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
        
        # Setup scan timer
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_scan)
        self.progress = 0
        
    def toggle_scan(self):
        if not self.is_scanning:
            self.start_scan()
        else:
            self.stop_scan()
    
    def start_scan(self):
        self.is_scanning = True
        self.start_button.setText("Stop Scan")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #FF3B30;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF2D55;
            }
        """)
        
        self.result_box.clear()
        self.progress = 0
        self.progress_bar.setValue(0)
        self.scan_timer.start(100)
        self.log_message("Starting threat scan...", "info")
        
    def stop_scan(self):
        self.is_scanning = False
        self.scan_timer.stop()
        self.start_button.setText("Start Threat Scan")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0066CC;
            }
        """)
        self.log_message("Scan stopped by user.", "warning")
        
    def update_scan(self):
        self.progress += 1
        self.progress_bar.setValue(self.progress)
        
        if self.progress >= 100:
            self.stop_scan()
            self.complete_scan()
            return
            
        # Simulate scanning different components
        if self.progress == 25:
            self.scan_processes()
        elif self.progress == 50:
            self.scan_network()
        elif self.progress == 75:
            self.scan_system()
            
    def scan_processes(self):
        suspicious_count = 0
        process_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                mem = proc.info['memory_info'].rss / (1024 * 1024)  # MB
                name = proc.info['name']
                process_count += 1
                
                if mem > 500:  # High memory usage threshold
                    suspicious_count += 1
                    self.log_message(
                        f"High memory usage detected: {name} ({mem:.2f} MB)", 
                        "warning"
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        self.processes_card.update_value(str(process_count))
        return suspicious_count
        
    def scan_network(self):
        connection_count = 0
        suspicious_count = 0
        
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED' and conn.raddr:
                connection_count += 1
                ip, port = conn.raddr
                
                if not ip.startswith(("192.168.", "127.0.0.1", "10.")):
                    suspicious_count += 1
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        hostname = "Unknown"
                    self.log_message(
                        f"External connection detected: {ip}:{port} ({hostname})", 
                        "warning"
                    )
                    
        self.connections_card.update_value(str(connection_count))
        return suspicious_count
        
    def scan_system(self):
        # Simulate system scan findings
        suspicious_count = 0
        
        # CPU usage check
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 90:
            suspicious_count += 1
            self.log_message(f"High CPU usage detected: {cpu_percent}%", "warning")
            
        # Memory usage check
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            suspicious_count += 1
            self.log_message(f"High memory usage detected: {mem.percent}%", "warning")
            
        return suspicious_count
        
    def complete_scan(self):
        total_threats = int(self.threats_card.value_label.text())
        self.last_scan_card.update_value(datetime.now().strftime("%H:%M:%S"))
        
        if total_threats == 0:
            self.log_message("Scan complete. No threats detected.", "success")
        else:
            self.log_message(
                f"Scan complete. {total_threats} potential threats detected.", 
                "error"
            )
            
    def log_message(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Set color based on message level
        color = {
            "info": "#FFFFFF",
            "warning": "#FFA500",
            "error": "#FF3B30",
            "success": "#32CD32"
        }.get(level, "#FFFFFF")
        
        html_message = f'<span style="color: {color}">[{timestamp}] {message}</span><br>'
        self.result_box.insertHtml(html_message)
        
        # Update threat count for warnings and errors
        if level in ["warning", "error"]:
            current_threats = int(self.threats_card.value_label.text())
            self.threats_card.update_value(str(current_threats + 1))
        
        # Log to file
        getattr(logger, level)(message)

def get_threat_detection_tab():
    return ThreatDetectionModule()
