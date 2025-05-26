import platform
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from loguru import logger

def get_compliance_tab():
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Compliance Tracking Module")
    start_button = QPushButton("Run Compliance Check")
    result_box = QTextEdit()
    result_box.setReadOnly(True)

    layout.addWidget(label)
    layout.addWidget(start_button)
    layout.addWidget(result_box)
    tab.setLayout(layout)

    def check_compliance():
        result_box.clear()
        result_box.append("Running compliance checks...\n")
        logger.info("Compliance check started.")

        system = platform.system()

        if system == "Windows":
            check_firewall_windows(result_box)
            check_defender_windows(result_box)
            check_updates_windows(result_box)
            check_bitlocker_windows(result_box)
            check_password_policy_windows(result_box)

        elif system == "Linux":
            result_box.append("Linux Compliance Checks:\n")
            check_ufw_firewall(result_box)
            check_clamav(result_box)
            check_unattended_upgrades(result_box)
            check_luks_encryption(result_box)

        elif system == "Darwin":
            result_box.append("macOS Compliance Checks:\n")
            check_macos_firewall(result_box)
            check_filevault(result_box)
            check_macos_updates(result_box)
            result_box.append("[!] Password policy checks are not implemented on macOS.")

        else:
            result_box.append(f"[!] Unsupported OS: {system}")

        logger.info("Compliance check completed.")

    start_button.clicked.connect(check_compliance)
    return tab


# --- Windows compliance checks ---
def check_firewall_windows(result_box):
    try:
        output = subprocess.check_output(
            'netsh advfirewall show allprofiles state', shell=True, text=True)
        if "ON" in output:
            result_box.append("[✓] Windows Firewall is enabled.")
        else:
            result_box.append("[✗] Windows Firewall is disabled.")
    except Exception as e:
        result_box.append(f"[!] Could not check Windows Firewall: {e}")

def check_defender_windows(result_box):
    try:
        output = subprocess.check_output(
            'powershell Get-MpComputerStatus | Select-Object -ExpandProperty AMServiceEnabled',
            shell=True, text=True)
        if 'True' in output:
            result_box.append("[✓] Windows Defender Antivirus service is running.")
        else:
            result_box.append("[✗] Windows Defender Antivirus service is not running.")
    except Exception as e:
        result_box.append(f"[!] Could not check Windows Defender status: {e}")

def check_updates_windows(result_box):
    try:
        output = subprocess.check_output(
            'powershell "(Get-WindowsUpdateLog)"', shell=True, text=True)
        # The above is complicated, so we simplify here
        result_box.append("[!] Windows Update status check is complex and not implemented.")
    except Exception as e:
        result_box.append(f"[!] Could not check Windows Updates: {e}")

def check_bitlocker_windows(result_box):
    try:
        output = subprocess.check_output(
            'manage-bde -status', shell=True, text=True)
        if "Percentage Encrypted: 100%" in output:
            result_box.append("[✓] BitLocker encryption is enabled.")
        else:
            result_box.append("[✗] BitLocker encryption is not fully enabled.")
    except Exception as e:
        result_box.append(f"[!] Could not check BitLocker status: {e}")

def check_password_policy_windows(result_box):
    try:
        output = subprocess.check_output(
            'net accounts', shell=True, text=True)
        result_box.append("[Windows Password Policy]")
        result_box.append(output)
    except Exception as e:
        result_box.append(f"[!] Could not check Windows password policy: {e}")


# --- Linux compliance checks ---
def check_ufw_firewall(result_box):
    try:
        ufw_status = subprocess.check_output("ufw status", shell=True, text=True)
        if "Status: active" in ufw_status:
            result_box.append("[✓] UFW firewall is active.")
        else:
            result_box.append("[✗] UFW firewall is inactive.")
    except Exception as e:
        result_box.append(f"[!] Could not check UFW firewall: {e}")

def check_clamav(result_box):
    try:
        clamav_status = subprocess.check_output(
            "systemctl is-active clamav-daemon", shell=True, text=True).strip()
        if clamav_status == "active":
            result_box.append("[✓] ClamAV antivirus is running.")
        else:
            result_box.append("[✗] ClamAV antivirus is not running.")
    except Exception as e:
        result_box.append(f"[!] Could not check ClamAV status: {e}")

def check_unattended_upgrades(result_box):
    try:
        update_status = subprocess.check_output(
            "systemctl is-active unattended-upgrades", shell=True, text=True).strip()
        if update_status == "active":
            result_box.append("[✓] Automatic updates are enabled.")
        else:
            result_box.append("[✗] Automatic updates are disabled.")
    except Exception as e:
        result_box.append(f"[!] Could not check automatic updates: {e}")

def check_luks_encryption(result_box):
    try:
        luks_status = subprocess.check_output(
            "lsblk -o NAME,TYPE,MOUNTPOINT | grep crypt", shell=True, text=True).strip()
        if luks_status:
            result_box.append("[✓] Disk encryption (LUKS) is enabled.")
        else:
            result_box.append("[✗] Disk encryption (LUKS) not detected.")
    except Exception as e:
        result_box.append(f"[!] Could not check disk encryption: {e}")


# --- macOS compliance checks ---
def check_macos_firewall(result_box):
    try:
        fw_status = subprocess.check_output(
            "defaults read /Library/Preferences/com.apple.alf globalstate", shell=True, text=True).strip()
        if fw_status == "1":
            result_box.append("[✓] macOS Firewall is enabled.")
        else:
            result_box.append("[✗] macOS Firewall is disabled.")
    except Exception as e:
        result_box.append(f"[!] Could not check macOS Firewall status: {e}")

def check_filevault(result_box):
    try:
        fv_status = subprocess.check_output("fdesetup status", shell=True, text=True).strip()
        if "FileVault is On" in fv_status:
            result_box.append("[✓] FileVault encryption is enabled.")
        else:
            result_box.append("[✗] FileVault encryption is disabled.")
    except Exception as e:
        result_box.append(f"[!] Could not check FileVault status: {e}")

def check_macos_updates(result_box):
    try:
        auto_update = subprocess.check_output(
            "defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled", shell=True, text=True).strip()
        if auto_update == "1":
            result_box.append("[✓] Automatic updates are enabled.")
        else:
            result_box.append("[✗] Automatic updates are disabled.")
    except Exception as e:
        result_box.append(f"[!] Could not check automatic updates: {e}")
