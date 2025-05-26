from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel

def get_incident_log_tab():
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Incident Log Viewer")
    layout.addWidget(label)

    result_box = QTextEdit()
    result_box.setReadOnly(True)
    result_box.setText("This is a test. Incident log tab loaded.")
    layout.addWidget(result_box)

    tab.setLayout(layout)
    return tab
