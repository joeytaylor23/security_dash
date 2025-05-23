from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
import psutil

def get_system_monitor_tab():
    widget = QWidget()
    layout = QVBoxLayout()
    
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    layout.addWidget(QLabel(f"CPU Usage: {cpu}%"))
    layout.addWidget(QLabel(f"Memory Usage: {mem}%"))
    layout.addWidget(QLabel(f"Disk Usage: {disk}%"))

    widget.setLayout(layout)
    return widget
