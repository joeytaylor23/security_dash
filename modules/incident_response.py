import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, 
    QMessageBox, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QLineEdit
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from loguru import logger
from .gui_components import (StyledLabel, StyledButton, StyledGroupBox, 
                           DataCard, COLORS)

class IncidentResponseModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_database()
        self.setup_ui()
        self.incident_count = 0
        self.critical_count = 0
        self.setup_auto_refresh()
        
    def setup_database(self):
        try:
            # Connect to database with proper settings for persistence
            self.conn = sqlite3.connect('incidents.db', check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.conn.cursor()
            
            # Create incidents table if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    status TEXT NOT NULL
                )
            ''')
            self.conn.commit()
            logger.info("Database setup completed successfully")
        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            QMessageBox.critical(self, "Database Error", 
                               "Failed to initialize database. Please check the logs.")
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = StyledLabel("Incident Response Center", is_title=True)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Stats section
        stats_layout = QHBoxLayout()
        
        self.total_incidents_card = DataCard("Total Incidents", "0")
        self.critical_incidents_card = DataCard("Critical Incidents", "0")
        self.last_incident_card = DataCard("Last Incident", "Never")
        self.response_time_card = DataCard("Avg Response Time", "N/A")
        
        for card in [self.total_incidents_card, self.critical_incidents_card, 
                    self.last_incident_card, self.response_time_card]:
            stats_layout.addWidget(card)
            
        layout.addLayout(stats_layout)
        
        # Create tab widget for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #1E1E1E;
                color: white;
                padding: 8px 16px;
                border: 1px solid #333333;
            }
            QTabBar::tab:selected {
                background-color: #007AFF;
            }
        """)
        
        # New Incident Tab
        self.tabs.addTab(self.create_new_incident_tab(), "New Incident")
        
        # Incident Log Tab
        self.tabs.addTab(self.create_incident_log_tab(), "Incident Log")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Initial refresh
        self.refresh_incident_data()
        
    def create_new_incident_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Incident Details Group
        details_group = StyledGroupBox("Incident Details")
        details_layout = QVBoxLayout()
        
        # Top row with all elements in horizontal layout
        top_row_layout = QHBoxLayout()
        
        # Subject Label
        subject_label = StyledLabel("Subject:")
        top_row_layout.addWidget(subject_label)
        
        # Subject Input
        self.subject_input = QLineEdit()
        self.subject_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        top_row_layout.addWidget(self.subject_input)
        
        # Severity Label
        severity_label = StyledLabel("Severity Level:")
        top_row_layout.addWidget(severity_label)
        
        # Severity Selection
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["Low", "Medium", "High", "Critical"])
        self.severity_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E1E1E;
                color: white;
                selection-background-color: #007AFF;
            }
        """)
        
        # Set colors for severity items
        for i in range(self.severity_combo.count()):
            severity = self.severity_combo.itemText(i)
            color = "green" if severity == "Low" else "yellow" if severity == "Medium" else "orange" if severity == "High" else "red"
            self.severity_combo.setItemData(i, QColor(color), Qt.ForegroundRole)
        
        top_row_layout.addWidget(self.severity_combo)
        
        # Add some spacing between elements
        top_row_layout.addStretch()
        
        # Add the top row layout to the main layout
        details_layout.addLayout(top_row_layout)
        
        # Description Input
        description_label = StyledLabel("Incident Description:")
        self.description_text = QTextEdit()
        self.description_text.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        details_layout.addWidget(description_label)
        details_layout.addWidget(self.description_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        self.save_button = StyledButton("Save Incident")
        self.save_button.clicked.connect(self.save_incident)
        self.clear_button = StyledButton("Clear Form")
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

        # Status Messages
        status_group = StyledGroupBox("Status Messages")
        status_layout = QVBoxLayout()
        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        self.status_box.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        status_layout.addWidget(self.status_box)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        tab.setLayout(layout)
        return tab
        
    def create_incident_log_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Filter Controls
        filter_layout = QHBoxLayout()
        
        # Severity Filter
        severity_label = StyledLabel("Filter by Severity:")
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["All", "Critical", "High", "Medium", "Low"])
        self.severity_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }
        """)
        filter_layout.addWidget(severity_label)
        filter_layout.addWidget(self.severity_filter)
        
        # Search Filter
        search_label = StyledLabel("Search:")
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Search in subject or description...")
        self.search_filter.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 5px;
                min-width: 200px;
            }
        """)
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_filter)
        
        # Sort Order
        sort_label = StyledLabel("Sort by:")
        self.sort_filter = QComboBox()
        self.sort_filter.addItems(["Time (Newest)", "Time (Oldest)", "Severity (High-Low)", "Severity (Low-High)"])
        self.sort_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        filter_layout.addWidget(sort_label)
        filter_layout.addWidget(self.sort_filter)
        
        # Apply Filter Button
        self.apply_filter_btn = StyledButton("Apply Filters")
        self.apply_filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.apply_filter_btn)
        
        layout.addLayout(filter_layout)
        
        # Incident Log Tree
        self.log_tree = QTreeWidget()
        self.log_tree.setHeaderLabels(["Time", "Subject", "Severity", "Description", "Status"])
        self.log_tree.setAlternatingRowColors(True)
        self.log_tree.setStyleSheet("""
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
        self.log_tree.setColumnWidth(0, 150)  # Time
        self.log_tree.setColumnWidth(1, 250)  # Subject
        self.log_tree.setColumnWidth(2, 100)  # Severity
        self.log_tree.setColumnWidth(3, 300)  # Description
        
        layout.addWidget(self.log_tree)
        
        # Refresh button
        refresh_button = StyledButton("Refresh Log")
        refresh_button.clicked.connect(self.refresh_incident_data)
        layout.addWidget(refresh_button)
        
        tab.setLayout(layout)
        return tab
        
    def setup_auto_refresh(self):
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_incident_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def save_incident(self):
        subject = self.subject_input.text().strip()
        severity = self.severity_combo.currentText()
        description = self.description_text.toPlainText().strip()
        
        if not subject:
            QMessageBox.warning(self, "Validation Error", 
                              "Please provide an incident subject.")
            return

        if not description:
            QMessageBox.warning(self, "Validation Error", 
                              "Please provide an incident description.")
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"Attempting to save incident - Subject: {subject}, Severity: {severity}")
            
            # Check if database connection is valid
            if not self.conn:
                raise Exception("Database connection is not initialized")
                
            self.cursor.execute('''
                INSERT INTO incidents (subject, severity, description, timestamp, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (subject, severity, description, timestamp, "New"))
            
            # Verify the insert was successful
            if self.cursor.rowcount == 0:
                raise Exception("No rows were inserted")
                
            self.conn.commit()
            logger.info("Incident saved successfully")
            
            self.log_message(f"New incident logged: {subject} - {severity}")
            self.clear_form()
            self.refresh_incident_data()
            
        except sqlite3.Error as e:
            error_msg = f"SQLite error occurred: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to save incident: {error_msg}")
        except Exception as e:
            error_msg = f"Failed to save incident: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Database Error", error_msg)
            
    def clear_form(self):
        self.subject_input.clear()
        self.severity_combo.setCurrentIndex(0)
        self.description_text.clear()
        
    def refresh_incident_data(self):
        try:
            # Ensure connection is still valid
            if not self.conn:
                self.setup_database()
                
            # Clear existing items
            self.log_tree.clear()
            
            # Fetch incidents from database
            self.cursor.execute('''
                SELECT timestamp, subject, severity, description, status 
                FROM incidents 
                ORDER BY timestamp DESC
            ''')
            incidents = self.cursor.fetchall()
            
            # Update stats
            self.incident_count = len(incidents)
            self.critical_count = sum(1 for i in incidents if i[2] == "Critical")
            
            self.total_incidents_card.update_value(str(self.incident_count))
            self.critical_incidents_card.update_value(str(self.critical_count))
            
            if incidents:
                self.last_incident_card.update_value(incidents[0][0])
            
            # Populate tree
            for incident in incidents:
                item = QTreeWidgetItem(incident)
                severity = incident[2]
                if severity == "Critical":
                    item.setForeground(2, QColor("red"))
                elif severity == "High":
                    item.setForeground(2, QColor("orange"))
                elif severity == "Medium":
                    item.setForeground(2, QColor("yellow"))
                else:
                    item.setForeground(2, QColor("green"))
                self.log_tree.addTopLevelItem(item)
                
        except sqlite3.Error as e:
            logger.error(f"Database error during refresh: {str(e)}")
            self.log_message("Failed to refresh incident data - Database error", "error")
            # Try to reconnect
            self.setup_database()
        except Exception as e:
            logger.error(f"Failed to refresh incident data: {str(e)}")
            self.log_message("Failed to refresh incident data", "error")
            
    def log_message(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        if level == "error":
            logger.error(message)
            self.status_box.append(f'<span style="color: #FF4444;">{formatted_message}</span>')
        else:
            # Check if message contains severity level and color it accordingly
            if "Critical" in message:
                self.status_box.append(f'<span style="color: red;">{formatted_message}</span>')
            elif "High" in message:
                self.status_box.append(f'<span style="color: orange;">{formatted_message}</span>')
            elif "Medium" in message:
                self.status_box.append(f'<span style="color: yellow;">{formatted_message}</span>')
            elif "Low" in message:
                self.status_box.append(f'<span style="color: green;">{formatted_message}</span>')
            else:
                self.status_box.append(formatted_message)
            
        # Scroll to bottom
        self.status_box.verticalScrollBar().setValue(
            self.status_box.verticalScrollBar().maximum()
        )

    def apply_filters(self):
        try:
            # Get filter values
            severity_filter = self.severity_filter.currentText()
            search_text = self.search_filter.text().lower()
            sort_order = self.sort_filter.currentText()
            
            # Clear existing items
            self.log_tree.clear()
            
            # Fetch all incidents
            self.cursor.execute('''
                SELECT timestamp, subject, severity, description, status 
                FROM incidents
            ''')
            incidents = self.cursor.fetchall()
            
            # Apply filters
            filtered_incidents = []
            for incident in incidents:
                # Apply severity filter
                if severity_filter != "All" and incident[2] != severity_filter:
                    continue
                    
                # Apply search filter
                if search_text and search_text not in incident[1].lower() and search_text not in incident[3].lower():
                    continue
                    
                filtered_incidents.append(incident)
            
            # Apply sorting
            if sort_order == "Time (Newest)":
                filtered_incidents.sort(key=lambda x: x[0], reverse=True)
            elif sort_order == "Time (Oldest)":
                filtered_incidents.sort(key=lambda x: x[0])
            elif sort_order == "Severity (High-Low)":
                severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
                filtered_incidents.sort(key=lambda x: severity_order[x[2]])
            elif sort_order == "Severity (Low-High)":
                severity_order = {"Critical": 3, "High": 2, "Medium": 1, "Low": 0}
                filtered_incidents.sort(key=lambda x: severity_order[x[2]])
            
            # Populate tree with filtered and sorted incidents
            for incident in filtered_incidents:
                item = QTreeWidgetItem(incident)
                severity = incident[2]
                if severity == "Critical":
                    item.setForeground(2, QColor("red"))
                elif severity == "High":
                    item.setForeground(2, QColor("orange"))
                elif severity == "Medium":
                    item.setForeground(2, QColor("yellow"))
                else:
                    item.setForeground(2, QColor("green"))
                self.log_tree.addTopLevelItem(item)
                
        except Exception as e:
            logger.error(f"Failed to apply filters: {str(e)}")
            self.log_message("Failed to apply filters", "error")

    def focusInEvent(self, event):
        """Handle when the window gains focus"""
        super().focusInEvent(event)
        self.refresh_incident_data()
        
    def closeEvent(self, event):
        """Handle when the window is closed"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")
        super().closeEvent(event)

def get_incident_response_tab():
    return IncidentResponseModule()
