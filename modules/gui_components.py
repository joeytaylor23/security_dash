from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, 
                            QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QFont, QColor, QLinearGradient

# Color scheme
COLORS = {
    'primary': QColor(0, 122, 255),
    'secondary': QColor(64, 156, 255),
    'background': QColor(18, 18, 18),
    'surface': QColor(30, 30, 30),
    'text': QColor(255, 255, 255),
    'text_secondary': QColor(180, 180, 180),
    'success': QColor(50, 205, 50),
    'warning': QColor(255, 165, 0),
    'error': QColor(255, 69, 58)
}

class StyledGroupBox(QGroupBox):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                background-color: #1E1E1E;
                border: 2px solid #333333;
                border-radius: 8px;
                margin-top: 1em;
                padding: 8px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)

class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0066CC;
            }
            QPushButton:pressed {
                background-color: #005299;
            }
        """)

class StyledLabel(QLabel):
    def __init__(self, text="", is_title=False, parent=None):
        super().__init__(text, parent)
        size = "16px" if is_title else "12px"
        weight = "bold" if is_title else "normal"
        self.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {size};
                font-weight: {weight};
                padding: 4px;
            }}
        """)

class DataCard(QFrame):
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout()
        self.title_label = StyledLabel(title)
        self.value_label = StyledLabel(value, is_title=True)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)
    
    def update_value(self, value):
        self.value_label.setText(str(value))

def apply_dark_theme(widget):
    widget.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: white;
        }
        QTabWidget::pane {
            border: 1px solid #333333;
            background-color: #1E1E1E;
        }
        QTabBar::tab {
            background-color: #1E1E1E;
            color: white;
            padding: 8px 16px;
            border: 1px solid #333333;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #007AFF;
        }
        QScrollBar:vertical {
            border: none;
            background-color: #1E1E1E;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #333333;
            border-radius: 5px;
        }
    """) 