import os
import sys
from loguru import logger
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Setup logging
logger.add("logs/activity.log", rotation="500 KB")
logger.info("App started")

# Import your dashboard modules
from modules.system_monitor import get_system_monitor_tab
from modules.network_monitor import get_network_monitor_tab
from modules.threat_detection import get_threat_detection_tab
from modules.risk_assessment import get_risk_assessment_tab
from modules.asset_management import get_asset_management_tab
from modules.compliance import get_compliance_tab
from modules.incident_response import get_incident_response_tab
#from modules.view_incidents import get_incident_log_tab

class SecurityDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Dashboard")
        self.setGeometry(100, 100, 1000, 700)

        # Create the tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Setup and add all tabs
        self.setup_tabs()

    def setup_tabs(self):
       self.tabs.addTab(get_system_monitor_tab(), "System Monitor")
       self.tabs.addTab(get_network_monitor_tab(), "Network Monitor")
       self.tabs.addTab(get_threat_detection_tab(), "Threat Detection")
       self.tabs.addTab(get_risk_assessment_tab(), "Risk Assessment")
       self.tabs.addTab(get_asset_management_tab(), "Asset Management")
       self.tabs.addTab(get_compliance_tab(), "Compliance Tracking")
       self.tabs.addTab(get_incident_response_tab(), "Incident Response")
       #self.tabs.addTab(get_incident_log_tab(), "Incident Log")


if __name__ == "__main__":
    app = QApplication(
        sys.argv)
    window = SecurityDashboard()
    window.show()
    sys.exit(app.exec_())
