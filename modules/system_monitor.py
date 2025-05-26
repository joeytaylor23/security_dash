import psutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QGroupBox
from PyQt5.QtCore import QTimer, Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QFont, QColor
from PyQt5.QtWidgets import QLabel


class CircularProgress(QWidget):
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.value = 0
        self.setMinimumSize(160, 160)
        self.setStyleSheet("background-color: black; color: white;")
        
    def setValue(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen_width = 10  # ✅ Define it here

        # Rectangle where the arc will be drawn
        rect = QRectF(pen_width + 10, 10, self.width() - 2 * (pen_width + 10), self.height() - 60)

        # Background arc (light gray)
        base_pen = QPen(QColor(230, 230, 230), pen_width)
        base_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(base_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Foreground arc (progress)
        progress_pen = QPen(QColor(0, 122, 255), pen_width)
        progress_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(progress_pen)
        painter.drawArc(rect, -90 * 16, -int((self.value / 100) * 360) * 16)

        # Percentage text
        font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(Qt.black))
        text = f"{int(self.value)}%"
        text_rect = self.rect().adjusted(3, -20, 3, -20) 
        painter.drawText(text_rect, Qt.AlignCenter, text)

        # Label text below
        painter.setPen(QColor(80, 80, 80))
        label_font = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(label_font)
        painter.drawText(QRectF(0, self.height() - 30, self.width(), 20), Qt.AlignCenter, self.label_text)

def get_system_monitor_tab():
    tab = QWidget()
    layout = QVBoxLayout()
    grid = QGridLayout()

    # Create widgets
    cpu_widget = CircularProgress("CPU Usage")
    ram_widget = CircularProgress("RAM Usage")
    disk_widget = CircularProgress("Disk Usage")
    battery_widget = CircularProgress("Battery")

    # Add to layout
    grid.addWidget(wrap_in_group(cpu_widget), 0, 0)
    grid.addWidget(wrap_in_group(ram_widget), 0, 1)
    grid.addWidget(wrap_in_group(disk_widget), 1, 0)
    grid.addWidget(wrap_in_group(battery_widget), 1, 1)

    layout.addLayout(grid)
    tab.setLayout(layout)

    def update_stats():
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        battery = psutil.sensors_battery().percent if psutil.sensors_battery() else None

        cpu_widget.setValue(int(cpu))
        ram_widget.setValue(int(ram))
        disk_widget.setValue(int(disk))
        if battery is not None:
            battery_widget.setValue(int(battery))
        else:
            battery_widget.setValue(0)
            battery_widget.label_text = "Battery: N/A"

    timer = QTimer()
    timer.timeout.connect(update_stats)
    timer.start(1500)

    update_stats()

    return tab


def wrap_in_group(widget):
    box = QGroupBox()
    layout = QVBoxLayout()
    layout.addWidget(widget, alignment=Qt.AlignCenter)
    box.setLayout(layout)
    return box
