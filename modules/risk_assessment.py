import psutil
import platform
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QProgressBar)
from PyQt5.QtCore import QTimer, Qt
from loguru import logger
from .gui_components import (StyledLabel, StyledButton, StyledGroupBox, 
                           DataCard, COLORS)

class RiskGauge(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setTextVisible(True)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333333;
                border-radius: 5px;
                text-align: center;
                background-color: #1E1E1E;
                height: 25px;
            }
            QProgressBar::chunk {
                border-radius: 3px;
            }
        """)
        
    def update_risk(self, value):
        self.setValue(value)
        
        if value < 30:
            color = COLORS['success'].name()
            self.setFormat("Low Risk (%p%)")
        elif value < 70:
            color = COLORS['warning'].name()
            self.setFormat("Moderate Risk (%p%)")
        else:
            color = COLORS['error'].name()
            self.setFormat("High Risk (%p%)")
            
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #333333;
                border-radius: 5px;
                text-align: center;
                background-color: #1E1E1E;
                height: 25px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)

class RiskAssessmentModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.is_assessing = False
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = StyledLabel("Security Risk Assessment", is_title=True)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Stats section
        stats_layout = QHBoxLayout()
        
        self.risk_score_card = DataCard("Risk Score", "0%")
        self.issues_card = DataCard("Issues Found", "0")
        self.last_scan_card = DataCard("Last Assessment", "Never")
        self.system_health_card = DataCard("System Health", "Unknown")
        
        for card in [self.risk_score_card, self.issues_card, 
                    self.last_scan_card, self.system_health_card]:
            stats_layout.addWidget(card)
            
        layout.addLayout(stats_layout)
        
        # Risk gauge section
        gauge_group = StyledGroupBox("Overall Risk Level")
        gauge_layout = QVBoxLayout()
        
        self.risk_gauge = RiskGauge()
        gauge_layout.addWidget(self.risk_gauge)
        
        # Control button
        self.assess_button = StyledButton("Run Risk Assessment")
        self.assess_button.clicked.connect(self.toggle_assessment)
        gauge_layout.addWidget(self.assess_button)
        
        gauge_group.setLayout(gauge_layout)
        layout.addWidget(gauge_group)
        
        # Findings section
        findings_group = StyledGroupBox("Assessment Findings")
        findings_layout = QVBoxLayout()
        
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
        findings_layout.addWidget(self.result_box)
        findings_group.setLayout(findings_layout)
        layout.addWidget(findings_group)
        
        self.setLayout(layout)
        
    def toggle_assessment(self):
        if not self.is_assessing:
            self.start_assessment()
        else:
            self.stop_assessment()
            
    def start_assessment(self):
        self.is_assessing = True
        self.assess_button.setText("Stop Assessment")
        self.assess_button.setStyleSheet("""
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
        self.issues_card.update_value("0")
        self.log_message("Starting risk assessment...", "info")
        self.run_assessment()
        
    def stop_assessment(self):
        self.is_assessing = False
        self.assess_button.setText("Run Risk Assessment")
        self.assess_button.setStyleSheet("""
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
        
    def run_assessment(self):
        score = 0
        max_score = 8  # Maximum possible risk score
        issues = 0
        
        # System uptime assessment
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
        self.log_message(f"System Uptime: {uptime}", "info")
        
        if uptime.total_seconds() > 7 * 24 * 60 * 60:  # 7 days
            score += 1
            issues += 1
            self.log_message("High uptime without reboot - System may be missing critical updates", "warning")
            
        # OS version assessment
        os_info = f"{platform.system()} {platform.release()}"
        self.log_message(f"Operating System: {os_info}", "info")
        
        # Memory usage assessment
        mem = psutil.virtual_memory()
        self.log_message(f"Memory Usage: {mem.percent}%", "info")
        
        if mem.percent > 90:
            score += 2
            issues += 1
            self.log_message("Critical memory usage - System stability at risk", "error")
        elif mem.percent > 80:
            score += 1
            issues += 1
            self.log_message("High memory usage detected", "warning")
            
        # Process assessment
        high_mem_processes = 0
        for proc in psutil.process_iter(['name', 'memory_info']):
            try:
                if proc.info['memory_info'].rss / (1024 * 1024) > 500:  # 500MB
                    high_mem_processes += 1
            except:
                continue
                
        self.log_message(f"High Memory Processes: {high_mem_processes}", "info")
        if high_mem_processes > 5:
            score += 1
            issues += 1
            self.log_message("Multiple high-memory processes detected", "warning")
            
        # Network assessment
        ext_conn = 0
        for conn in psutil.net_connections(kind='inet'):
            if (conn.status == 'ESTABLISHED' and conn.raddr and 
                not conn.raddr.ip.startswith(("192.168.", "127.0.0.1", "10."))):
                ext_conn += 1
                
        self.log_message(f"External Connections: {ext_conn}", "info")
        if ext_conn > 5:
            score += 2
            issues += 1
            self.log_message("High number of external connections - Potential security risk", "error")
        elif ext_conn > 3:
            score += 1
            issues += 1
            self.log_message("Multiple external connections detected", "warning")
            
        # CPU usage assessment
        cpu_percent = psutil.cpu_percent()
        self.log_message(f"CPU Usage: {cpu_percent}%", "info")
        
        if cpu_percent > 90:
            score += 1
            issues += 1
            self.log_message("High CPU usage detected", "warning")
            
        # Calculate final risk percentage
        risk_percent = int((score / max_score) * 100)
        self.risk_gauge.update_risk(risk_percent)
        self.risk_score_card.update_value(f"{risk_percent}%")
        self.issues_card.update_value(str(issues))
        self.last_scan_card.update_value(datetime.datetime.now().strftime("%H:%M:%S"))
        
        # Update system health
        if risk_percent < 30:
            health = "Good"
            level = "success"
        elif risk_percent < 70:
            health = "Fair"
            level = "warning"
        else:
            health = "Poor"
            level = "error"
            
        self.system_health_card.update_value(health)
        
        # Final assessment message
        self.log_message(
            f"Assessment complete - Overall Risk Level: {risk_percent}%", 
            level
        )
        
        self.stop_assessment()
        
    def log_message(self, message, level="info"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Set color based on message level
        color = {
            "info": "#FFFFFF",
            "warning": "#FFA500",
            "error": "#FF3B30",
            "success": "#32CD32"
        }.get(level, "#FFFFFF")
        
        html_message = f'<span style="color: {color}">[{timestamp}] {message}</span><br>'
        self.result_box.insertHtml(html_message)
        
        # Log to file
        getattr(logger, level)(message)

def get_risk_assessment_tab():
    return RiskAssessmentModule()
