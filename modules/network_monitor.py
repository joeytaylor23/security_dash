from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt5.QtCore import QTimer, Qt
import socket
import psutil
from .gui_components import StyledLabel, StyledButton, StyledGroupBox, DataCard

class NetworkMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = StyledLabel("Network Status Monitor", is_title=True)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Main stats section
        stats_group = StyledGroupBox("Network Statistics")
        stats_layout = QHBoxLayout()
        
        self.sent_card = DataCard("Data Sent", "0 MB")
        self.recv_card = DataCard("Data Received", "0 MB")
        self.hostname_card = DataCard("Hostname", socket.gethostname())
        self.ip_card = DataCard("IP Address", "Loading...")
        
        for card in [self.hostname_card, self.ip_card, self.sent_card, self.recv_card]:
            stats_layout.addWidget(card)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Interfaces section
        interfaces_group = StyledGroupBox("Network Interfaces")
        interfaces_layout = QVBoxLayout()
        
        # Create a scroll area for interfaces
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.interfaces_widget = QWidget()
        self.interfaces_layout = QVBoxLayout()
        self.interfaces_widget.setLayout(self.interfaces_layout)
        scroll.setWidget(self.interfaces_widget)
        
        interfaces_layout.addWidget(scroll)
        interfaces_group.setLayout(interfaces_layout)
        layout.addWidget(interfaces_group)
        
        # Refresh button
        refresh_btn = StyledButton("Refresh")
        refresh_btn.clicked.connect(self.update_network_info)
        layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        
        # Setup timer for auto-refresh
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_network_info)
        self.timer.start(2000)  # Update every 2 seconds
        
        # Initial update
        self.update_network_info()
    
    def update_network_info(self):
        # Update hostname & IP
        try:
            primary_ip = socket.gethostbyname(socket.gethostname())
            self.ip_card.update_value(primary_ip)
        except socket.gaierror:
            self.ip_card.update_value("Unavailable")
        
        # Update network I/O stats
        net_io = psutil.net_io_counters()
        mb_sent = net_io.bytes_sent / (1024 ** 2)
        mb_recv = net_io.bytes_recv / (1024 ** 2)
        
        self.sent_card.update_value(f"{mb_sent:.2f} MB")
        self.recv_card.update_value(f"{mb_recv:.2f} MB")
        
        # Clear previous interface widgets
        for i in reversed(range(self.interfaces_layout.count())): 
            widget = self.interfaces_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add interface information
        for iface_name, addrs in psutil.net_if_addrs().items():
            iface_group = StyledGroupBox(iface_name)
            iface_layout = QVBoxLayout()
            
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    addr_label = StyledLabel(f"IPv4: {addr.address}")
                    iface_layout.addWidget(addr_label)
                elif addr.family == socket.AF_INET6:
                    addr_label = StyledLabel(f"IPv6: {addr.address}")
                    iface_layout.addWidget(addr_label)
            
            # Get interface statistics
            try:
                stats = psutil.net_if_stats()[iface_name]
                status = "Up" if stats.isup else "Down"
                speed = f"{stats.speed} Mbps" if stats.speed > 0 else "Unknown"
                stats_label = StyledLabel(f"Status: {status} | Speed: {speed}")
                iface_layout.addWidget(stats_label)
            except:
                pass
            
            iface_group.setLayout(iface_layout)
            self.interfaces_layout.addWidget(iface_group)

def get_network_monitor_tab():
    return NetworkMonitor()
