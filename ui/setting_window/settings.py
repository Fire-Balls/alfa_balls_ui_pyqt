from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton, QFrame
)

class PlaceholderInterface(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QPushButton(f"{title} content"))
