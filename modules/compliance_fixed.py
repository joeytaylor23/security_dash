import platform
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
                            QTextEdit, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, QTimer
from loguru import logger
from .gui_components import (StyledLabel, StyledButton, StyledGroupBox, 
                           DataCard, COLORS)

class ComplianceModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.is_checking = False
        self.current_check = 0
        self.total_checks = self.get_total_checks()
        
    def setup_ui(self):
        layout = QVBoxLayout()

        # Header
        header = StyledLabel("Security Compliance Center", is_title=True)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Stats section
        stats_layout = QHBoxLayout()
        
        self.compliance_score_card = DataCard("Compliance Score", "0%")
        self.checks_passed_card = DataCard("Checks Passed", "0/0")
        self.critical_issues_card = DataCard("Critical Issues", "0")
        self.last_check_card = DataCard("Last Check", "Never")
        
        for card in [self.compliance_score_card, self.checks_passed_card, 
                    self.critical_issues_card, self.last_check_card]:
            stats_layout.addWidget(card)
            
        layout.addLayout(stats_layout)
        
        # Progress section
        progress_group = StyledGroupBox("Compliance Check Progress")
        progress_layout = QVBoxLayout()
        
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
        progress_layout.addWidget(self.progress_bar)
        
        # Control button
        self.check_button = StyledButton("Run Compliance Check")
        self.check_button.clicked.connect(self.toggle_check)
        progress_layout.addWidget(self.check_button)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Results section
        results_group = StyledGroupBox("Compliance Results")
        results_layout = QVBoxLayout()
        
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Check", "Status", "Details"])
        self.results_tree.setAlternatingRowColors(True)
        self.results_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 5px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:alternate {
                background-color: #262626;
            }
            QTreeWidget::item:selected {
                background-color: #007AFF;
            }
            QHeaderView::section {
                background-color: #333333;
                color: white;
                padding: 5px;
                border: none;
            }
        """)
        self.results_tree.setColumnWidth(0, 200)
        self.results_tree.setColumnWidth(1, 100)
        
        results_layout.addWidget(self.results_tree)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Details section
        details_group = StyledGroupBox("Check Details")
        details_layout = QVBoxLayout()
        
        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        self.details_box.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        details_layout.addWidget(self.details_box)
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        self.setLayout(layout)
        
    def get_total_checks(self):
        system = platform.system()
        if system == "Windows":
            return 5  # Windows checks
        elif system == "Linux":
            return 4  # Linux checks
        elif system == "Darwin":
            return 3  # macOS checks
        return 0
        
    def toggle_check(self):
        if not self.is_checking:
            self.start_check()
        else:
            self.stop_check()
            
    def start_check(self):
        self.is_checking = True
        self.check_button.setText("Stop Check")
        self.check_button.setStyleSheet("""
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
        
        # Reset UI
        self.results_tree.clear()
        self.details_box.clear()
        self.current_check = 0
        self.progress_bar.setValue(0)
        self.checks_passed_card.update_value("0/0")
        self.critical_issues_card.update_value("0")
        
        # Start checks
        self.log_message("Starting compliance checks...", "info")
        self.check_compliance()
        
    def stop_check(self):
        self.is_checking = False
        self.check_button.setText("Run Compliance Check")
        self.check_button.setStyleSheet("""
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
        
    def check_compliance(self):
        system = platform.system()

        if system == "Windows":
            self.check_windows_compliance()
        elif system == "Linux":
            self.check_linux_compliance()
        elif system == "Darwin":
            self.check_macos_compliance()
        else:
            self.log_message(f"Unsupported OS: {system}", "error")
            
    def check_windows_compliance(self):
        self.add_check_result("Windows Firewall", self.check_firewall_windows())
        self.add_check_result("Windows Defender", self.check_defender_windows())
        self.add_check_result("Windows Updates", self.check_updates_windows())
        self.add_check_result("BitLocker Encryption", self.check_bitlocker_windows())
        self.add_check_result("Password Policy", self.check_password_policy_windows())
        self.complete_check()
        
    def check_linux_compliance(self):
        self.add_check_result("UFW Firewall", self.check_ufw_firewall())
        self.add_check_result("ClamAV Antivirus", self.check_clamav())
        self.add_check_result("Automatic Updates", self.check_unattended_upgrades())
        self.add_check_result("LUKS Encryption", self.check_luks_encryption())
        self.complete_check()
        
    def check_macos_compliance(self):
        self.add_check_result("macOS Firewall", self.check_macos_firewall())
        self.add_check_result("FileVault Encryption", self.check_filevault())
        self.add_check_result("Automatic Updates", self.check_macos_updates())
        self.complete_check()
        
    def add_check_result(self, check_name, result):
        status, details = result
        
        # Create tree item
        item = QTreeWidgetItem([check_name, status, details])
        
        # Set status color
        if status == "PASS":
            item.setForeground(1, COLORS['success'])
        elif status == "FAIL":
            item.setForeground(1, COLORS['error'])
        else:
            item.setForeground(1, COLORS['warning'])
            
        self.results_tree.addTopLevelItem(item)
        
        # Update progress
        self.current_check += 1
        progress = int((self.current_check / self.total_checks) * 100)
        self.progress_bar.setValue(progress)
        
        # Update stats
        passed = len([i for i in range(self.results_tree.topLevelItemCount()) 
                     if self.results_tree.topLevelItem(i).text(1) == "PASS"])
        total = self.results_tree.topLevelItemCount()
        self.checks_passed_card.update_value(f"{passed}/{total}")
        
        critical = len([i for i in range(self.results_tree.topLevelItemCount()) 
                       if self.results_tree.topLevelItem(i).text(1) == "FAIL"])
        self.critical_issues_card.update_value(str(critical))
        
        # Log the result
        level = "success" if status == "PASS" else "error" if status == "FAIL" else "warning"
        self.log_message(f"{check_name}: {status} - {details}", level)
        
    def complete_check(self):
        passed = len([i for i in range(self.results_tree.topLevelItemCount()) 
                     if self.results_tree.topLevelItem(i).text(1) == "PASS"])
        total = self.results_tree.topLevelItemCount()
        
        if total > 0:
            score = int((passed / total) * 100)
            self.compliance_score_card.update_value(f"{score}%")
            
            if score >= 80:
                level = "success"
                message = "High compliance level achieved"
            elif score >= 60:
                level = "warning"
                message = "Moderate compliance level - improvements needed"
            else:
                level = "error"
                message = "Low compliance level - immediate action required"
                
            self.log_message(f"Compliance check complete - {message}", level)
            
        self.last_check_card.update_value(datetime.now().strftime("%H:%M:%S"))
        self.stop_check()
        
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
        self.details_box.insertHtml(html_message)
        
        # Log to file
        getattr(logger, level)(message)
        
    # Windows compliance checks
    def check_firewall_windows(self):
        try:
            output = subprocess.check_output(
                'netsh advfirewall show allprofiles state', shell=True, text=True)
            if "ON" in output:
                return "PASS", "Firewall is enabled"
            return "FAIL", "Firewall is disabled"
        except Exception as e:
            return "ERROR", f"Could not check firewall: {e}"

    def check_defender_windows(self):
        try:
            output = subprocess.check_output(
                'powershell Get-MpComputerStatus | Select-Object -ExpandProperty AMServiceEnabled',
                shell=True, text=True)
            if 'True' in output:
                return "PASS", "Defender service is running"
            return "FAIL", "Defender service is not running"
        except Exception as e:
            return "ERROR", f"Could not check Defender: {e}"

    def check_updates_windows(self):
        try:
            output = subprocess.check_output(
                'powershell "(Get-WindowsUpdateLog)"', shell=True, text=True)
            return "WARN", "Update status check requires manual review"
        except Exception as e:
            return "ERROR", f"Could not check updates: {e}"

    def check_bitlocker_windows(self):
        try:
            output = subprocess.check_output(
                'manage-bde -status', shell=True, text=True)
            if "Percentage Encrypted: 100%" in output:
                return "PASS", "BitLocker is fully enabled"
            return "FAIL", "BitLocker is not fully enabled"
        except Exception as e:
            return "ERROR", f"Could not check BitLocker: {e}"
                
    def check_password_policy_windows(self):
        try:
            output = subprocess.check_output('net accounts', shell=True, text=True)
            return "WARN", "Password policy requires manual review"
        except Exception as e:
            return "ERROR", f"Could not check password policy: {e}"
            
    # Linux compliance checks
    def check_ufw_firewall(self):
        try:
            output = subprocess.check_output("ufw status", shell=True, text=True)
            if "Status: active" in output:
                return "PASS", "UFW firewall is active"
            return "FAIL", "UFW firewall is inactive"
        except Exception as e:
            return "ERROR", f"Could not check UFW: {e}"

    def check_clamav(self):
        try:
            status = subprocess.check_output(
                "systemctl is-active clamav-daemon", shell=True, text=True).strip()
            if status == "active":
                return "PASS", "ClamAV is running"
            return "FAIL", "ClamAV is not running"
        except Exception as e:
            return "ERROR", f"Could not check ClamAV: {e}"

    def check_unattended_upgrades(self):
        try:
            status = subprocess.check_output(
                "systemctl is-active unattended-upgrades", shell=True, text=True).strip()
            if status == "active":
                return "PASS", "Automatic updates are enabled"
            return "FAIL", "Automatic updates are disabled"
        except Exception as e:
            return "ERROR", f"Could not check updates: {e}"

    def check_luks_encryption(self):
        try:
            output = subprocess.check_output(
                "lsblk -o NAME,TYPE,MOUNTPOINT | grep crypt", shell=True, text=True).strip()
            if output:
                return "PASS", "LUKS encryption is enabled"
            return "FAIL", "LUKS encryption not detected"
        except Exception as e:
            return "ERROR", f"Could not check LUKS: {e}"
                
    # macOS compliance checks
    def check_macos_firewall(self):
        try:
            status = subprocess.check_output(
                "defaults read /Library/Preferences/com.apple.alf globalstate",
                shell=True, text=True).strip()
            if status == "1":
                return "PASS", "Firewall is enabled"
            return "FAIL", "Firewall is disabled"
        except Exception as e:
            return "ERROR", f"Could not check firewall: {e}"
            
    def check_filevault(self):
        try:
            status = subprocess.check_output(
                "fdesetup status", shell=True, text=True).strip()
            if "FileVault is On" in status:
                return "PASS", "FileVault is enabled"
            return "FAIL", "FileVault is disabled"
        except Exception as e:
            return "ERROR", f"Could not check FileVault: {e}"
            
    def check_macos_updates(self):
        try:
            status = subprocess.check_output(
                "defaults read /Library/Preferences/com.apple.commerce AutoUpdate",
                shell=True, text=True).strip()
            if status == "1":
                return "PASS", "Automatic updates are enabled"
            return "FAIL", "Automatic updates are disabled"
        except Exception as e:
            return "ERROR", f"Could not check updates: {e}"

def get_compliance_tab():
    return ComplianceModule() 