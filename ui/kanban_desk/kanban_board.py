from __future__ import annotations
import sys
import dateutil.parser as parser
from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import Qt, QEvent, QMimeData, QPoint, QTimer
from PySide6.QtGui import QDrag, QCursor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QVBoxLayout, QLabel, \
    QAbstractItemView, QPushButton, QScrollArea, QApplication

from network.new.models import Board, Issue, IssueShortcut, Project, BoardShortcut
from network.new.operations import ServiceOperations
from ui.kanban_desk.task.add_task_dialog import AddTaskDialog
from ui.kanban_desk.task.create_task_item import create_task_item


class KanbanColumn(QListWidget):
    def __init__(self, title, board: KanbanBoard, status_id, parent=None):
        super().__init__(parent)
        self.setObjectName("kanban_column")
        self.status_id = status_id
        # Разрешение на передвижение и отключение скрола
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedWidth(225)
        self.drag_source_column = None
        # Убрать пунктирное выделении при нажатии
        self.setFocusPolicy(Qt.NoFocus)
        # расстояние между тасками
        self.setSpacing(5)

        # фикс бага при повторном выделении
        self.board = board
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.itemSelectionChanged.connect(self.on_selection_changed)

        # Столбцы
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("margin-bottom: 5px; font-family: 'Arial'")

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self)
        self.container = QWidget()
        self.container.setLayout(layout)

    def widget(self):
        return self.container

    def eventFilter(self, source, event):
        if event.type() == QEvent.FocusOut:
            self.clearSelection()  # Убираем выделение при потере фокуса
        return super().eventFilter(source, event)

    def on_selection_changed(self):
        self.board.clear_all_selections(except_column=self)

    def dropEvent(self, event):
        super().dropEvent(event)
        target_column = self
        item = target_column.item(target_column.count() - 1)  # последний добавленный
        task_data = item.data(Qt.UserRole)
        print(task_data)
        print(type(task_data))
        if not task_data:
            return
        issue_back = ServiceOperations.get_issue(0, 0, task_data.get('id'))
        ServiceOperations.update_issue(0, 0, issue_back.id, issue_back.title, issue_back.description,
                                       issue_back.code, issue_back.type, status_id=target_column.status_id,
                                       author_id=issue_back.author.id, assignee_id=issue_back.assignee.id,
                                       deadline=issue_back.deadline.strftime('%Y-%m-%dT%H:%M:%S'), tags=issue_back.tags)
        project_back_short = ServiceOperations.get_project_by_name(target_column.board.project_name,
                                                                   target_column.board.user_id)
        project_back_full = ServiceOperations.get_project(project_back_short.id)
        res_board = None
        for board in project_back_full.boards:
            if board.id == target_column.board.board_id:
                res_board = board
        target_column.board.set_project_and_board(project_back_full, res_board)

    def startDrag(self, supported_actions):
        self.board.drag_source_column = self  # запоминаем откуда
        super().startDrag(supported_actions)


class KanbanBoard(QWidget):
    AUTOSCROLL_THRESHOLD = 50  # Пиксели от края, когда начинать автопрокрутку
    AUTOSCROLL_SPEED = 20      # Скорость прокрутки (пиксели за интервал)
    AUTOSCROLL_INTERVAL = 20   # Интервал таймера автопрокрутки (миллисекунды)

    def __init__(self, user_id, board_id, parent):
        super().__init__()
        self.user_id = user_id
        self.board_id = board_id
        self.columns = {}
        self.parent = parent

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("kanban_scroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Основные макеты
        self.board_container = DroppableBoardContainer(self)
        self.board_container.kanban_board = self  # Добавляем обратную ссылку
        self.board_layout = self.board_container.layout()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.board_layout)
        self.scroll_area.setWidget(self.board_container)
        self.main_layout.addWidget(self.scroll_area)

        self.columns = {}

        if self.parent.user_role == "OWNER":
            self.add_column_button = QPushButton("Создать колонку")
            self.add_column_button.clicked.connect(self.show_add_column_dialog)
            self.main_layout.addWidget(self.add_column_button, alignment=Qt.AlignRight)

        # Кнопка добавления задачи
        self.add_task_button = QPushButton("Добавить задачу")
        self.add_task_button.clicked.connect(self.show_add_task_dialog)
        self.main_layout.addWidget(self.add_task_button, alignment=Qt.AlignRight)

        self.setLayout(self.main_layout)

        # Таймер для автопрокрутки
        self.autoscroll_timer = QTimer(self)
        self.autoscroll_timer.timeout.connect(self.autoscroll)
        self.autoscroll_direction = 0  # -1: влево, 1: вправо, 0: нет

        self.dragging = False # Флаг, чтобы понимать, когда происходит перетаскивание

    def add_task(self, issue: IssueShortcut | Issue):
        if issue.status.name not in self.columns:
            print(f"[ERROR] Колонка '{issue.status.name}' не найдена")
            return

        print(f"[ADD TASK] Добавление '{issue.title}' в колонку '{issue.status}' с номером {issue.code}")

        # Создаем задачу с новыми параметрами
        item, widget = create_task_item(
            issue_id=issue.id,
            issue_type=issue.type,
            number=issue.code,
            title=issue.title,
            tags=issue.tags,
            is_important=False,
            executor=issue.assignee
        )

        column = self.columns[issue.status.name]
        column.addItem(item)
        column.setItemWidget(item, widget)

    def show_add_task_dialog(self):
        dialog = AddTaskDialog(self.parent.users_list, self)
        if dialog.exec():
            (name, description, tags, is_important, start_datetime,
             end_datetime, executor, files, issue_type) = dialog.get_data()
            parsed_end_datetime = parser.parse(str(end_datetime.toPython())).isoformat()
            all_users = ServiceOperations.get_project(ServiceOperations.get_board(0, self.board_id).project_id).users
            executor = executor.split(", Роль:")[0]
            assignee = None
            for user in all_users:
                if user.full_name == executor:
                    assignee = user

            if name:
                saved_task = ServiceOperations.create_new_issue(
                    project_id=0,
                    board_id=self.board_id,
                    title=name,
                    description=description,
                    author_id=self.user_id,
                    assignee_id=assignee.id if assignee is not None else None,
                    deadline=parsed_end_datetime,
                    files_paths=files,
                    tags=tags,
                    issue_type=issue_type
                )
                retrieved_task = ServiceOperations.get_issue(0, self.board_id, saved_task.id)
                self.add_task(retrieved_task)

    def clear_all_selections(self, except_column=None):
        for column in self.columns.values():
            if column is not except_column:
                column.clearSelection()

    def load_tasks(self, board: Board):
        """Принимает models.Board"""

        if not isinstance(board, Board):
            return

        for issue in board.issues:
            self.add_task(issue)

    def clear_board(self):
        """Полностью очищает доску, включая все колонки и задачи"""
        # 1. Удаляем все задачи из всех колонок
        for column in self.columns.values():
            print(column)
            column.clear()  # Очищаем QListWidget

        # 2. Удаляем сами колонки
        for i in reversed(range(self.board_layout.count())):
            item = self.board_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
                self.board_layout.removeItem(item)

        # 3. Очищаем внутренние структуры
        self.columns.clear()

        # 4. Принудительное обновление UI
        self.update()
        QApplication.processEvents()

    def show_add_column_dialog(self):
        column_name, ok = QInputDialog.getText(self, "Новая колонка", "Введите название колонки:")
        if ok and column_name.strip():
            self.add_column(column_name.strip(), None)

    def add_column(self, name: str, status_id: int | None):
        if name in self.columns:
            print(f"Колонка '{name}' уже существует")
            return
        print('add_column', name)

        if status_id is None:
            status_to_create = ServiceOperations.create_new_status(name, 0, self.board_id)
        else:
            status_to_create = ServiceOperations.get_status(0, 0, status_id)


        column = KanbanColumn(status_to_create.name, self, status_to_create.id)
        column.setObjectName(status_to_create.name)
        self.columns[status_to_create.name] = column
        wrapper = ColumnWrapperWidget(column)
        self.board_layout.addWidget(wrapper)

    def reorder_column_by_name(self, name: str, drop_pos: QPoint):
        column_wrapper = None
        for i in range(self.board_layout.count()):
            item = self.board_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, ColumnWrapperWidget):
                if widget.column.title_label.text() == name:
                    column_wrapper = widget
                    self.board_layout.removeWidget(widget)
                    break

        if column_wrapper:
            insert_index = self._find_insert_index(drop_pos)
            self.board_layout.insertWidget(insert_index, column_wrapper)

    def _find_insert_index(self, drop_pos: QPoint) -> int:
        for i in range(self.board_layout.count()):
            item = self.board_layout.itemAt(i)
            widget = item.widget()
            if widget:
                if drop_pos.x() < widget.x() + widget.width() // 2:
                    return i
        return self.board_layout.count()

    def set_project_name(self, project_name):
        self.project_name = project_name

    def get_all_columns(self):
        return self.findChildren(KanbanColumn)

    def set_project_and_board(self, project: Project, board_shortcut: BoardShortcut):
        """Устанавливает проект и доску, загружает задачи"""
        self.board_id = board_shortcut.id
        self.clear_board()

        if not project:
            return

        full_board = ServiceOperations.get_board(project.id, board_shortcut.id)
        # Создаем колонки
        for status in full_board.statuses:
            if status.name not in self.columns:
                self.add_column(status.name, status.id)

        # Загружаем задачи
        self.load_tasks(full_board)

    def autoscroll(self):
        """Выполняет прокрутку ScrollArea в зависимости от направления."""
        scrollbar = self.scroll_area.horizontalScrollBar()
        if self.autoscroll_direction == -1:  # Влево
            scrollbar.setValue(max(0, scrollbar.value() - self.AUTOSCROLL_SPEED))
        elif self.autoscroll_direction == 1:  # Вправо
            scrollbar.setValue(min(scrollbar.maximum(), scrollbar.value() + self.AUTOSCROLL_SPEED))


class ColumnWrapperWidget(QWidget):
    def __init__(self, column: KanbanColumn, parent=None):
        super().__init__(parent)
        self.drag_start_position = None
        self.column = column
        self.setAcceptDrops(True)
        self.kanban_board = self # Добавляем атрибут для хранения ссылки на KanbanBoard
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.column.widget())
        self.setLayout(layout)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            if self.kanban_board:
                self.kanban_board.dragging = True


    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and (event.pos() - self.drag_start_position).manhattanLength() > 10:
            if self.kanban_board:
                self.kanban_board.dragging = True
            mime_data = QMimeData()
            mime_data.setText(self.column.title_label.text())

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(event.pos())
            drag.exec(Qt.MoveAction)
            if self.kanban_board:
                self.kanban_board.dragging = False

class DroppableBoardContainer(QWidget):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.setAcceptDrops(True)
        # self.kanban_board = None  # Ссылка на KanbanBoard
        self.kanban_board = board
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        print(f"Event  dragEnterEvent : {event.type(),    event.pos().x()}")
        if event.mimeData().hasText():
            event.acceptProposedAction()
            if self.kanban_board:
                self.kanban_board.dragging = True  # Устанавливаем флаг начала перетаскивания
            # Запускаем таймер автопрокрутки
            self.start_autoscroll_if_needed(event.pos().x())



    def dragMoveEvent(self, event):
        print(f"Event   dragMoveEvent: {event.type(),   event.pos().x()}")
        """Обработчик события перетаскивания (вызывается при перемещении объекта над виджетом)."""
        if self.kanban_board:
            # Обновляем направление и запускаем автопрокрутку, если нужно
            self.start_autoscroll_if_needed(event.pos().x())
        event.acceptProposedAction()



    def dragLeaveEvent(self, event):
        """Обработчик события покидания виджета перетаскиваемым объектом."""
        if self.kanban_board:
             self.kanban_board.dragging = False
        # Останавливаем таймер при покидании виджета
        self.stop_autoscroll()
        event.accept()



    def dropEvent(self, event):
        print(f"Event: {event.type()}")
        text = event.mimeData().text()
        self.board.reorder_column_by_name(text, event.pos())
        event.acceptProposedAction()
        if self.kanban_board:
            self.kanban_board.dragging = False # Сбрасываем флаг после завершения перетаскивания
        self.stop_autoscroll()  # Останавливаем автопрокрутку после drop


    def start_autoscroll_if_needed(self, mouse_x):
        print(f"Mouse X: {mouse_x}, Threshold: {self.AUTOSCROLL_THRESHOLD}")
        """Определяет, нужно ли начинать автопрокрутку, и если да, то в каком направлении."""
        if not self.kanban_board or not self.kanban_board.dragging:  # Проверяем, идет ли перетаскивание
            print('ooooooooooooooo bro')
            return

        scroll_area_width = self.kanban_board.scroll_area.width()

        print('scroll_area_width', scroll_area_width)

        if mouse_x < self.kanban_board.AUTOSCROLL_THRESHOLD:
            self.start_autoscroll(-1)  # Влево
        elif mouse_x > scroll_area_width - self.kanban_board.AUTOSCROLL_THRESHOLD:
            self.start_autoscroll(1)  # Вправо
        else:
            self.stop_autoscroll()  # Остановить, если курсор внутри допустимой зоны



    def start_autoscroll(self, direction):
        """Запускает таймер автопрокрутки в заданном направлении."""
        if self.kanban_board.autoscroll_direction != direction:
            self.kanban_board.autoscroll_direction = direction
            self.kanban_board.autoscroll_timer.start(self.kanban_board.AUTOSCROLL_INTERVAL)


    def stop_autoscroll(self):
        """Останавливает таймер автопрокрутки."""
        if self.kanban_board.autoscroll_timer.isActive():
            self.kanban_board.autoscroll_timer.stop()
            self.kanban_board.autoscroll_direction = 0
