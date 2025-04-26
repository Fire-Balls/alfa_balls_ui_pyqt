from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить задачу")
        self.setFixedSize(300, 150)

        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Название задачи")

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Теги (через запятую)")

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Название задачи:"))
        layout.addWidget(self.task_name_input)
        layout.addWidget(QLabel("Теги:"))
        layout.addWidget(self.tags_input)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def get_data(self):
        name = self.task_name_input.text().strip()
        tags = [tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()]
        return name, tags