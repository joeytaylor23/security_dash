import psutil
import platform
import socket
import platform

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
from loguru import logger

def get_asset_management_tab():
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Asset Management Module")
    refresh_button = QPushButton("Refresh Assets")
    result_box = QTextEdit()
    result_box.setReadOnly(True)

    layout.addWidget(label)
    layout.addWidget(refresh_button)
    layout.addWidget(result_box)
    tab.setLayout(layout)

    def refresh_assets():
        result_box.clear()
        logger.info("Refreshing asset information...")

        hostname = socket.gethostname()
        os_info = f"{platform.system()} {platform.release()}"
        cpu_count = psutil.cpu_count(logical=True)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        users = psutil.users()
        net_if_addrs = psutil.net_if_addrs()

        result_box.append(f"Hostname: {hostname}")
        result_box.append(f"Operating System: {os_info}")
        result_box.append(f"CPU Cores: {cpu_count}")
        result_box.append(f"Total Memory: {mem.total // (1024**2)} MB")
        result_box.append(f"Available Memory: {mem.available // (1024**2)} MB")
        result_box.append(f"Disk Total: {disk.total // (1024**3)} GB")
        result_box.append(f"Disk Free: {disk.free // (1024**3)} GB")
        result_box.append("")

        result_box.append("Logged-in Users:")
        for user in users:
            result_box.append(f" - {user.name} since {user.started}")
        
        result_box.append("\nNetwork Interfaces:")
        for iface, addrs in net_if_addrs.items():
            result_box.append(f" - {iface}:")
            for addr in addrs:
                result_box.append(f"    {addr.family.name}: {addr.address}")
    
    try:
        import wmi
        c = wmi.WMI()
        result_box.append("\nUSB Devices:")
        for usb in c.Win32_USBControllerDevice():
            result_box.append(f" - {usb.Dependent}")
    except ImportError:
        result_box.append("\n[!] wmi module not found. Skipping USB detection.")
        
        logger.info("Asset information refreshed.")

    if platform.system() == "Windows":
        import winreg

    result_box.append("\nInstalled Programs:")

    uninstall_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    def enum_installed_programs(root, path):
        programs = []
        try:
            reg_key = winreg.OpenKey(root, path)
            for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                sub_key_name = winreg.EnumKey(reg_key, i)
                sub_key = winreg.OpenKey(reg_key, sub_key_name)
                try:
                    display_name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                    programs.append(display_name)
                except FileNotFoundError:
                    pass
                finally:
                    sub_key.Close()
            reg_key.Close()
        except Exception as e:
            result_box.append(f"[!] Error reading registry: {e}")
        return programs

    installed_programs = []
    for key in uninstall_keys:
        installed_programs.extend(enum_installed_programs(winreg.HKEY_LOCAL_MACHINE, key))

    # Remove duplicates and sort
    installed_programs = sorted(set(installed_programs))

    for prog in installed_programs:
        result_box.append(f" - {prog}")
    else:
        result_box.append("\n[!] Software inventory is currently only supported on Windows.")

   
    refresh_button.clicked.connect(refresh_assets)
    refresh_assets()  # Show initial data on load
    return tab
