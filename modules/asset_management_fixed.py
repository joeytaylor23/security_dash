import psutil
import platform
import socket
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QTextEdit, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt
from loguru import logger
from .gui_components import (StyledLabel, StyledButton, StyledGroupBox, 
                           DataCard, COLORS)

class AssetTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Asset", "Details"])
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
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
        self.setColumnWidth(0, 200)

class AssetManagementModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()

        # Header
        header = StyledLabel("Asset Management Center", is_title=True)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Stats section
        stats_layout = QHBoxLayout()
        
        self.total_memory_card = DataCard("Total Memory", "0 GB")
        self.disk_space_card = DataCard("Total Storage", "0 GB")
        self.cpu_cores_card = DataCard("CPU Cores", "0")
        self.last_scan_card = DataCard("Last Scan", "Never")
        
        for card in [self.total_memory_card, self.disk_space_card, 
                    self.cpu_cores_card, self.last_scan_card]:
            stats_layout.addWidget(card)
            
        layout.addLayout(stats_layout)
        
        # Create tab widget for different asset views
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
        
        # Hardware Assets Tab
        hardware_tab = QWidget()
        hardware_layout = QVBoxLayout()
        self.hardware_tree = AssetTreeWidget()
        hardware_layout.addWidget(self.hardware_tree)
        hardware_tab.setLayout(hardware_layout)
        self.tabs.addTab(hardware_tab, "Hardware")
        
        # Network Assets Tab
        network_tab = QWidget()
        network_layout = QVBoxLayout()
        self.network_tree = AssetTreeWidget()
        network_layout.addWidget(self.network_tree)
        network_tab.setLayout(network_layout)
        self.tabs.addTab(network_tab, "Network")
        
        # Software Assets Tab
        software_tab = QWidget()
        software_layout = QVBoxLayout()
        self.software_tree = AssetTreeWidget()
        software_layout.addWidget(self.software_tree)
        software_tab.setLayout(software_layout)
        self.tabs.addTab(software_tab, "Software")
        
        # Users Tab
        users_tab = QWidget()
        users_layout = QVBoxLayout()
        self.users_tree = AssetTreeWidget()
        users_layout.addWidget(self.users_tree)
        users_tab.setLayout(users_layout)
        self.tabs.addTab(users_tab, "Users")
        
        layout.addWidget(self.tabs)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.refresh_button = StyledButton("Refresh Assets")
        self.refresh_button.clicked.connect(self.refresh_assets)
        button_layout.addWidget(self.refresh_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initial refresh
        self.refresh_assets()
        
    def refresh_assets(self):
        self.refresh_hardware_assets()
        self.refresh_network_assets()
        self.refresh_software_assets()
        self.refresh_user_assets()
        self.update_stats()
        self.last_scan_card.update_value(datetime.now().strftime("%H:%M:%S"))
        logger.info("Asset information refreshed")
        
    def refresh_hardware_assets(self):
        self.hardware_tree.clear()
        
        # System Information
        system_item = QTreeWidgetItem(["System Information"])
        system_item.addChild(QTreeWidgetItem(["Hostname", socket.gethostname()]))
        system_item.addChild(QTreeWidgetItem(["OS", f"{platform.system()} {platform.release()}"]))
        system_item.addChild(QTreeWidgetItem(["Architecture", platform.machine()]))
        self.hardware_tree.addTopLevelItem(system_item)
        
        # CPU Information
        cpu_item = QTreeWidgetItem(["CPU"])
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_item.addChild(QTreeWidgetItem(["Cores", str(cpu_count)]))
        if cpu_freq:
            cpu_item.addChild(QTreeWidgetItem(["Frequency", f"{cpu_freq.current:.2f} MHz"]))
        cpu_item.addChild(QTreeWidgetItem(["Usage", f"{psutil.cpu_percent()}%"]))
        self.hardware_tree.addTopLevelItem(cpu_item)
        
        # Memory Information
        memory_item = QTreeWidgetItem(["Memory"])
        mem = psutil.virtual_memory()
        memory_item.addChild(QTreeWidgetItem(["Total", f"{mem.total // (1024**3)} GB"]))
        memory_item.addChild(QTreeWidgetItem(["Available", f"{mem.available // (1024**3)} GB"]))
        memory_item.addChild(QTreeWidgetItem(["Used", f"{mem.percent}%"]))
        self.hardware_tree.addTopLevelItem(memory_item)
        
        # Disk Information
        disk_item = QTreeWidgetItem(["Storage"])
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                part_item = QTreeWidgetItem([partition.device])
                part_item.addChild(QTreeWidgetItem(["Mount Point", partition.mountpoint]))
                part_item.addChild(QTreeWidgetItem(["Total", f"{usage.total // (1024**3)} GB"]))
                part_item.addChild(QTreeWidgetItem(["Used", f"{usage.percent}%"]))
                disk_item.addChild(part_item)
            except:
                continue
        self.hardware_tree.addTopLevelItem(disk_item)
        
        # Expand all items
        self.hardware_tree.expandAll()
        
    def refresh_network_assets(self):
        self.network_tree.clear()
        
        # Network Interfaces
        for iface, addrs in psutil.net_if_addrs().items():
            iface_item = QTreeWidgetItem([iface])
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    iface_item.addChild(QTreeWidgetItem(["IPv4", addr.address]))
                elif addr.family == socket.AF_INET6:
                    iface_item.addChild(QTreeWidgetItem(["IPv6", addr.address]))
                elif addr.family == psutil.AF_LINK:
                    iface_item.addChild(QTreeWidgetItem(["MAC", addr.address]))
            
            # Add interface statistics
            try:
                stats = psutil.net_if_stats()[iface]
                iface_item.addChild(QTreeWidgetItem(["Speed", f"{stats.speed} Mbps"]))
                iface_item.addChild(QTreeWidgetItem(["Status", "Up" if stats.isup else "Down"]))
            except:
                pass
                
            self.network_tree.addTopLevelItem(iface_item)
            
        # Network Connections
        connections_item = QTreeWidgetItem(["Active Connections"])
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                conn_item = QTreeWidgetItem([f"Connection {conn.pid if conn.pid else 'Unknown'}"])
                conn_item.addChild(QTreeWidgetItem(["Local", f"{conn.laddr.ip}:{conn.laddr.port}"]))
                if conn.raddr:
                    conn_item.addChild(QTreeWidgetItem(["Remote", f"{conn.raddr.ip}:{conn.raddr.port}"]))
                connections_item.addChild(conn_item)
        self.network_tree.addTopLevelItem(connections_item)
        
        self.network_tree.expandAll()
        
    def refresh_software_assets(self):
        self.software_tree.clear()

        if platform.system() == "Windows":
            try:
                import winreg

                def enum_installed_programs(root, key_path):
                    programs = []
                    try:
                        reg_key = winreg.OpenKey(root, key_path)
                        for i in range(winreg.QueryInfoKey(reg_key)[0]):
                            try:
                                sub_key_name = winreg.EnumKey(reg_key, i)
                                sub_key = winreg.OpenKey(reg_key, sub_key_name)
                                try:
                                    name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                    version = winreg.QueryValueEx(sub_key, "DisplayVersion")[0]
                                    publisher = winreg.QueryValueEx(sub_key, "Publisher")[0]
                                    programs.append((name, version, publisher))
                                except:
                                    pass
                                finally:
                                    sub_key.Close()
                            except:
                                continue
                        reg_key.Close()
                    except Exception as e:
                        logger.error(f"Error reading registry: {e}")
                    return programs

                paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
                ]
                
                programs = []
                for path in paths:
                    programs.extend(enum_installed_programs(winreg.HKEY_LOCAL_MACHINE, path))

                # Remove duplicates and sort
                programs = sorted(set(programs), key=lambda x: x[0].lower())
                
                # Add to tree
                for name, version, publisher in programs:
                    prog_item = QTreeWidgetItem([name])
                    prog_item.addChild(QTreeWidgetItem(["Version", version]))
                    prog_item.addChild(QTreeWidgetItem(["Publisher", publisher]))
                    self.software_tree.addTopLevelItem(prog_item)
                    
            except ImportError:
                error_item = QTreeWidgetItem(["Error"])
                error_item.addChild(QTreeWidgetItem(["Message", "Registry access not available"]))
                self.software_tree.addTopLevelItem(error_item)
        else:
            # Basic process listing for non-Windows systems
            processes = {}
            for proc in psutil.process_iter(['name', 'exe', 'cmdline']):
                try:
                    info = proc.info
                    if info['name'] not in processes and info['exe']:
                        processes[info['name']] = info['exe']
                except:
                    continue
            
            for name, path in sorted(processes.items()):
                prog_item = QTreeWidgetItem([name])
                prog_item.addChild(QTreeWidgetItem(["Path", path]))
                self.software_tree.addTopLevelItem(prog_item)
                
    def refresh_user_assets(self):
        self.users_tree.clear()
        
        # Current sessions
        sessions_item = QTreeWidgetItem(["Active Sessions"])
        for user in psutil.users():
            user_item = QTreeWidgetItem([user.name])
            user_item.addChild(QTreeWidgetItem(["Terminal", user.terminal or "N/A"]))
            user_item.addChild(QTreeWidgetItem(["Host", user.host or "local"]))
            started = datetime.fromtimestamp(user.started)
            user_item.addChild(QTreeWidgetItem(["Started", started.strftime("%Y-%m-%d %H:%M:%S")]))
            sessions_item.addChild(user_item)
        self.users_tree.addTopLevelItem(sessions_item)
        
        # User processes
        processes_item = QTreeWidgetItem(["User Processes"])
        user_procs = {}
        for proc in psutil.process_iter(['name', 'username']):
            try:
                username = proc.info['username']
                if username:
                    if username not in user_procs:
                        user_procs[username] = []
                    user_procs[username].append(proc.info['name'])
            except:
                continue
                
        for username, procs in sorted(user_procs.items()):
            user_item = QTreeWidgetItem([username])
            for proc in sorted(set(procs)):
                user_item.addChild(QTreeWidgetItem(["Process", proc]))
            processes_item.addChild(user_item)
            
        self.users_tree.addTopLevelItem(processes_item)
        self.users_tree.expandAll()
        
    def update_stats(self):
        # Update summary cards
        mem = psutil.virtual_memory()
        self.total_memory_card.update_value(f"{mem.total // (1024**3)} GB")
        
        total_storage = sum(
            psutil.disk_usage(p.mountpoint).total // (1024**3)
            for p in psutil.disk_partitions()
            if "fixed" in p.opts
        )
        self.disk_space_card.update_value(f"{total_storage} GB")
        
        self.cpu_cores_card.update_value(str(psutil.cpu_count(logical=True)))

def get_asset_management_tab():
    return AssetManagementModule() 