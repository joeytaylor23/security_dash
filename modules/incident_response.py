from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

def get_incident_response_tab():
    widget = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Threat Detection AI module will go here."))
    widget.setLayout(layout)
    return widget