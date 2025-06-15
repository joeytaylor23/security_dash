import psutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QFont
from .gui_components import COLORS, StyledGroupBox, StyledLabel, DataCard

class CircularProgress(QWidget):
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.value = 0
        self.setMinimumSize(160, 160)
        
    def setValue(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen_width = 10

        # Rectangle where the arc will be drawn
        rect = QRectF(pen_width + 10, 10, self.width() - 2 * (pen_width + 10), self.height() - 60)

        # Background arc
        base_pen = QPen(COLORS['surface'], pen_width)
        base_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(base_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Determine color based on value
        if self.value < 60:
            color = COLORS['success']
        elif self.value < 80:
            color = COLORS['warning']
        else:
            color = COLORS['error']

        # Foreground arc (progress)
        progress_pen = QPen(color, pen_width)
        progress_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(progress_pen)
        painter.drawArc(rect, -90 * 16, -int((self.value / 100) * 360) * 16)

        # Percentage text
        font = QFont("Segoe UI", 14, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(COLORS['text']))
        text = f"{int(self.value)}%"
        text_rect = self.rect().adjusted(3, -20, 3, -20)
        painter.drawText(text_rect, Qt.AlignCenter, text)

        # Label text below
        painter.setPen(COLORS['text_secondary'])
        label_font = QFont("Segoe UI", 10)
        painter.setFont(label_font)
        painter.drawText(QRectF(0, self.height() - 30, self.width(), 20), Qt.AlignCenter, self.label_text)

def get_system_monitor_tab():
    tab = QWidget()
    main_layout = QVBoxLayout()
    
    # Header
    header = StyledLabel("System Resource Monitor", is_title=True)
    header.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(header)

    # Create grid for circular progress widgets
    grid = QGridLayout()
    grid.setSpacing(20)

    # Create widgets
    cpu_widget = CircularProgress("CPU Usage")
    ram_widget = CircularProgress("RAM Usage")
    disk_widget = CircularProgress("Disk Usage")
    battery_widget = CircularProgress("Battery")

    # Create groups and add widgets
    cpu_group = StyledGroupBox("CPU Status")
    cpu_layout = QVBoxLayout()
    cpu_layout.addWidget(cpu_widget, alignment=Qt.AlignCenter)
    cpu_group.setLayout(cpu_layout)

    ram_group = StyledGroupBox("Memory Status")
    ram_layout = QVBoxLayout()
    ram_layout.addWidget(ram_widget, alignment=Qt.AlignCenter)
    ram_group.setLayout(ram_layout)

    disk_group = StyledGroupBox("Storage Status")
    disk_layout = QVBoxLayout()
    disk_layout.addWidget(disk_widget, alignment=Qt.AlignCenter)
    disk_group.setLayout(disk_layout)

    battery_group = StyledGroupBox("Power Status")
    battery_layout = QVBoxLayout()
    battery_layout.addWidget(battery_widget, alignment=Qt.AlignCenter)
    battery_group.setLayout(battery_layout)

    # Add groups to grid
    grid.addWidget(cpu_group, 0, 0)
    grid.addWidget(ram_group, 0, 1)
    grid.addWidget(disk_group, 1, 0)
    grid.addWidget(battery_group, 1, 1)

    # Add detailed stats section
    stats_layout = QHBoxLayout()
    
    # CPU Temperature card (if available)
    try:
        cpu_temp = psutil.sensors_temperatures()['coretemp'][0].current
        temp_card = DataCard("CPU Temperature", f"{cpu_temp:.1f}°C")
        stats_layout.addWidget(temp_card)
    except:
        pass
    
    # Memory Details card
    mem = psutil.virtual_memory()
    mem_total = f"{mem.total / (1024**3):.1f} GB"
    mem_card = DataCard("Total Memory", mem_total)
    stats_layout.addWidget(mem_card)
    
    # Disk Details card
    disk = psutil.disk_usage('/')
    disk_total = f"{disk.total / (1024**3):.1f} GB"
    disk_card = DataCard("Total Storage", disk_total)
    stats_layout.addWidget(disk_card)

    main_layout.addLayout(grid)
    main_layout.addLayout(stats_layout)
    tab.setLayout(main_layout)

    def update_stats():
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        battery = psutil.sensors_battery()
        
        cpu_widget.setValue(cpu)
        ram_widget.setValue(ram)
        disk_widget.setValue(disk)
        
        if battery:
            battery_widget.setValue(battery.percent)
        else:
            battery_widget.setValue(0)

    # Update every 1.5 seconds
    timer = QTimer()
    timer.timeout.connect(update_stats)
    timer.start(1500)

    # Initial update
    update_stats()

    return tab
