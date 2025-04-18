import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QListWidget, QListWidgetItem,
    QAbstractItemView, QMessageBox, QDialog, QDialogButtonBox, QComboBox
)
from PySide6.QtCore import Qt, QMimeData, Signal, Slot, QPoint
from PySide6.QtGui import QDrag

class TaskEditDialog(QDialog):
    task_moved = Signal(str)

    def __init__(self, parent=None, text="", columns=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать задачу")
        self.text = text
        self.columns = columns or []

        layout = QVBoxLayout()
        self.text_edit = QTextEdit(text)
        layout.addWidget(self.text_edit)

        self.column_combo = QComboBox()
        self.column_combo.addItems(self.columns)
        layout.addWidget(QLabel("Переместить в колонку:"))
        layout.addWidget(self.column_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept_changes)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_text(self):
        return self.text_edit.toPlainText()

    def accept_changes(self):
        destination_column = self.column_combo.currentText()
        self.task_moved.emit(destination_column)
        self.accept()

class TaskWidget(QWidget):
    task_edited = Signal(str)

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.text_label = QLabel(self.text)
        layout.addWidget(self.text_label)

        self.setLayout(layout)

    def setText(self, text):
        self.text = text
        self.text_label.setText(text)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_edit_dialog()

    def open_edit_dialog(self):
        # Access the KanbanBoard to get the list names
        kanban_board = self.parentWidget().parentWidget()  # Navigate to KanbanBoard

        if kanban_board:
            dialog = TaskEditDialog(self, self.text, columns=kanban_board.list_names)
            dialog.task_moved.connect(self.move_to_column)
            dialog.exec()
        else:
            print("KanbanBoard not found!")

    @Slot(str)
    def move_to_column(self, destination_column):
        # Get the KanbanBoard again (it might be necessary if structure changes)
        kanban_board = self.parentWidget().parentWidget()

        if kanban_board:
            kanban_board.move_task(self, destination_column)
            self.task_edited.emit(self.text)  # Emit signal for editing
        else:
            print("KanbanBoard not found for move!")

class KanbanBoard(QWidget):
    task_created = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kanban Board")
        self.list_names = ["To Do", "In Progress", "Done"]
        self.lists = {}
        self.init_ui()
        self.task_created.connect(self.add_task_from_dialog)

    def init_ui(self):
        layout = QHBoxLayout()

        for list_name in self.list_names:
            list_widget = QListWidget()
            list_widget.setAcceptDrops(True)
            list_widget.setDragEnabled(True)
            list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
            list_widget.setObjectName(list_name)
            layout.addWidget(list_widget)
            self.lists[list_name] = list_widget

        input_layout = QVBoxLayout()
        self.input_edit = QLineEdit()
        input_layout.addWidget(self.input_edit)

        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        input_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Task")
        self.delete_button.clicked.connect(self.delete_task)
        input_layout.addWidget(self.delete_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    @Slot(str)
    def add_task_from_dialog(self, text):
        if text:
            task = TaskWidget(text)
            item = QListWidgetItem()
            item.setSizeHint(task.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, task)
            self.lists["To Do"].addItem(item)
            self.lists["To Do"].setItemWidget(item, task)

    def add_task(self):
        dialog = TaskEditDialog(self, columns=self.list_names) # pass columns to the dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            text = dialog.get_text()
            self.task_created.emit(text)

    def delete_task(self):
        for list_name, list_widget in self.lists.items():
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                widget = list_widget.itemWidget(item)
                if isinstance(widget, TaskWidget) and widget.text_label.hasFocus():
                    list_widget.takeItem(i)
                    break

    def move_task(self, task, destination_column_name):
        source_list = None
        source_item_index = None

        for list_name, list_widget in self.lists.items():
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                widget = list_widget.itemWidget(item)
                if widget == task:
                    source_list = list_widget
                    source_item_index = i
                    break
            if source_list:
                break

        if source_list is None:
            print(f"Error: Could not find task in any list to move.")
            return

        destination_list = self.lists.get(destination_column_name)
        if destination_list is None:
            print(f"Error: Destination column '{destination_column_name}' not found.")
            return

        item = source_list.takeItem(source_item_index)

        destination_item = QListWidgetItem()
        destination_item.setSizeHint(task.sizeHint())
        destination_item.setData(Qt.ItemDataRole.UserRole, task)
        destination_list.addItem(destination_item)
        destination_list.setItemWidget(destination_item, task)

        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kanban_board = KanbanBoard()
    kanban_board.show()
    sys.exit(app.exec())
