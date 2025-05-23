from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import socket
import psutil


def get_network_monitor_tab():
    widget = QWidget()
    layout = QVBoxLayout()

    # Main labels
    hostname_label = QLabel()
    address_label = QLabel()
    sent_label = QLabel()
    recv_label = QLabel()

    # Hold dynamically created interface labels so we can clear them
    interface_labels = []

    def update_network_info():
        # Hostname & primary IP
        hostname = socket.gethostname()
        try:
            primary_ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            primary_ip = "Unavailable"

        # Network I/O stats
        net_io = psutil.net_io_counters()
        mb_sent = net_io.bytes_sent / (1024 ** 2)
        mb_recv = net_io.bytes_recv / (1024 ** 2)

        # Update the main labels
        hostname_label.setText(f"Hostname: {hostname}")
        address_label.setText(f"IP Address: {primary_ip}")
        sent_label.setText(f"Data Sent: {mb_sent:.2f} MB")
        recv_label.setText(f"Data Received: {mb_recv:.2f} MB")

        # Remove old interface labels
        for lbl in interface_labels:
            layout.removeWidget(lbl)
            lbl.deleteLater()
        interface_labels.clear()

        # Add a header for interfaces
        iface_header = QLabel("Active Interfaces:")
        layout.addWidget(iface_header)
        interface_labels.append(iface_header)

        # List each interface and its IPv4 address
        for iface_name, addrs in psutil.net_if_addrs().items():
            name_lbl = QLabel(f" • {iface_name}")
            layout.addWidget(name_lbl)
            interface_labels.append(name_lbl)

            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_lbl = QLabel(f"     IP: {addr.address}")
                    layout.addWidget(ip_lbl)
                    interface_labels.append(ip_lbl)

    # Add the main widgets
    for lbl in (hostname_label, address_label, sent_label, recv_label):
        layout.addWidget(lbl)

    # Refresh button
    refresh_btn = QPushButton("Refresh")
    refresh_btn.clicked.connect(update_network_info)
    layout.addWidget(refresh_btn)

    # Initial load
    update_network_info()

    widget.setLayout(layout)
    return widget
