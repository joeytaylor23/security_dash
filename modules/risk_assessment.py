import psutil
import platform
import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
from loguru import logger

def get_risk_assessment_tab():
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Risk Assessment Module")
    assess_button = QPushButton("Run Risk Assessment")
    result_box = QTextEdit()
    result_box.setReadOnly(True)

    layout.addWidget(label)
    layout.addWidget(assess_button)
    layout.addWidget(result_box)
    tab.setLayout(layout)

    def run_assessment():
        result_box.clear()
        logger.info("Running risk assessment...")

        score = 0
        findings = []

        # OS & uptime
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
        findings.append(f"System Uptime: {uptime}")
        if uptime.total_seconds() > 7 * 24 * 60 * 60:
            findings.append("[!] High uptime without reboot. Consider restarting for updates.")
            score += 1

        findings.append(f"Operating System: {platform.system()} {platform.release()}")

        # Memory usage
        mem = psutil.virtual_memory()
        findings.append(f"Memory Usage: {mem.percent}%")
        if mem.percent > 80:
            findings.append("[!] High memory usage.")
            score += 1

        # Suspicious processes
        high_mem_processes = 0
        for proc in psutil.process_iter(['name', 'memory_info']):
            try:
                if proc.info['memory_info'].rss / (1024 * 1024) > 100:
                    high_mem_processes += 1
            except:
                continue
        findings.append(f"Processes using >100MB: {high_mem_processes}")
        if high_mem_processes > 5:
            findings.append("[!] Too many high memory processes.")
            score += 1

        # Network connections
        ext_conn = sum(1 for c in psutil.net_connections(kind='inet') if c.status == 'ESTABLISHED' and c.raddr and not c.raddr.ip.startswith(("192.168.", "127.0.0.1")))
        findings.append(f"External Connections: {ext_conn}")
        if ext_conn > 3:
            findings.append("[!] Multiple external connections.")
            score += 1

        # Final risk level
        if score == 0:
            findings.append("\n[✓] Risk Level: LOW")
        elif score == 1:
            findings.append("\n[!] Risk Level: MODERATE")
        else:
            findings.append("\n[⚠️] Risk Level: HIGH")

        for line in findings:
            result_box.append(line)
            if "[!]" in line or "[⚠️]" in line:
                logger.warning(line)

    assess_button.clicked.connect(run_assessment)
    return tab
