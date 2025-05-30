from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy
)


class AnalyticWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Аналитика")
        self.resize(800, 600)
        self.setMinimumSize(500, 400)

        self.main_layout = QVBoxLayout(self)
        self.add_header()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        self.add_metrics_section(self.main_layout)
        self.add_chart_placeholder(self.main_layout)


    def add_metrics_section(self, parent_layout):
        metrics_frame = QFrame()
        metrics_layout = QHBoxLayout(metrics_frame)
        metrics_layout.setSpacing(30)

        # Пример метрик — можно подставлять реальные данные
        for label, value in [
            ("Всего задач", "24"),
            ("Выполнено", "15"),
            ("В работе", "6"),
            ("Ожидают", "3")
        ]:
            block = self.create_metric_block(label, value)
            metrics_layout.addWidget(block)

        parent_layout.addWidget(metrics_frame)

    def create_metric_block(self, label_text, value_text):
        block = QFrame()
        block.setFrameShape(QFrame.StyledPanel)
        block.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
        """)
        block.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(block)
        layout.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value_text)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_label.setFont(value_font)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(label)
        return block

    def add_chart_placeholder(self, parent_layout):
        chart = QLabel("График (placeholder)")
        chart.setStyleSheet("background-color: #ddd; border-radius: 8px;")
        chart.setAlignment(Qt.AlignCenter)
        chart.setMinimumHeight(300)
        parent_layout.addWidget(chart)

    def add_header(self):
        header_layout = QHBoxLayout()
        header_layout.addStretch()

        title_label = QLabel("Аналитика проекта")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignRight)

        header_layout.addWidget(title_label)
        self.main_layout.addLayout(header_layout)


