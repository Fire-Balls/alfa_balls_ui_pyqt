from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy, QToolTip, QScrollArea
)
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QHorizontalBarSeries
from network.new.operations import ServiceOperations


class AnalyticWindow(QWidget):
    def __init__(self, project_id: int):
        super().__init__()
        self.metrics_frame = None
        self.metrics_layout = None
        self.setWindowTitle("Аналитика")
        self.resize(800, 600)
        self.setMinimumSize(500, 400)
        self.project_id = project_id
        self.user_chart_view = None


        # Основной виджет и скролл
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_layout.setSpacing(15)

        self.scroll_area.setWidget(self.scroll_widget)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(self.scroll_area)

        self.add_header()
        self.user_chart_frame = QFrame()
        self.user_chart_layout = QVBoxLayout(self.user_chart_frame)
        self.user_chart_layout.setContentsMargins(0, 0, 0, 0)
        self.user_chart_layout.setSpacing(0)
        self.add_metrics_section(self.scroll_layout)
        self.scroll_layout.addWidget(self.user_chart_frame)
        self.add_horizontal_bar_chart(self.scroll_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics_section)
        self.timer.start(10000)  # 60 000 мс = 60 секунд


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
        self.scroll_layout.addLayout(header_layout)

    def add_metrics_section(self, parent_layout):
        self.metrics_frame = QFrame()
        self.metrics_layout = QHBoxLayout(self.metrics_frame)
        self.metrics_layout.setSpacing(30)

        parent_layout.addWidget(self.metrics_frame)

        self.update_metrics_section()  # первая загрузка

    def update_metrics_section(self):
        while self.metrics_layout.count():
            item = self.metrics_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Пересчитать статистику
        all_issues = ServiceOperations.get_project(self.project_id).issues
        issue_statuses = {
            "Всего задач": len(all_issues),
            "Выполнено": 0,
            "В работе": 0,
            "Ожидают": 0
        }

        for issue in all_issues:
            if issue.status.name == "DONE" and issue.status.common is True:
                issue_statuses["Выполнено"] += 1
            elif issue.status.name == "TODO" and issue.status.common is True:
                issue_statuses["Ожидают"] += 1
            else:
                issue_statuses["В работе"] += 1

        for label, value in issue_statuses.items():
            block = self.create_metric_block(label, str(value))
            self.metrics_layout.addWidget(block)

        self.update_user_task_chart()

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

    def update_user_task_chart(self):
        # Очистить старый график
        while self.user_chart_layout.count():
            item = self.user_chart_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        all_issues = ServiceOperations.get_project(self.project_id).issues
        person_issues = {}

        for issue in all_issues:
            if issue.assignee is None:
                continue
            if issue.status.name != "DONE" or not issue.status.common:
                continue
            assignee = issue.assignee.full_name
            person_issues[assignee] = person_issues.get(assignee, 0) + 1

        if not person_issues:
            return

        bar_set = QBarSet("Выполненные задачи")
        bar_set.append(list(person_issues.values()))

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Количество выполненных задач по участникам")

        axis_x = QBarCategoryAxis()
        names = list(person_issues.keys())
        axis_x.append(names)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTitleText("Задачи")
        axis_y.setLabelFormat("%d")
        axis_y.setTickType(QValueAxis.TicksDynamic)
        axis_y.setTickInterval(1)
        axis_y.setMinorTickCount(0)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)

        self.user_chart_layout.addWidget(chart_view)
        self.user_chart_view = chart_view

        def on_bar_clicked(index):
            name = names[index]
            value = bar_set.at(index)
            bar_pos = chart.mapToPosition(QPointF(index, value), series)
            global_pos = chart_view.mapToGlobal(chart_view.mapFromScene(bar_pos))
            QToolTip.showText(global_pos, f"<b>{name}</b><br>Задач: {int(value)}", chart_view)

        bar_set.clicked.connect(on_bar_clicked)

    def add_horizontal_bar_chart(self, parent_layout):
        # Тестовые значения:
        bug_count = 3  # Тип Bug сюда засунуть
        story_count = 1  # Тип Story сюда засунуть
        task_count = 6 # Тип Task сюда засунуть

        set1 = QBarSet("Bug")
        set2 = QBarSet("Story")
        set3 = QBarSet("Task")

        set1 << bug_count
        set2 << story_count
        set3 << task_count

        series = QHorizontalBarSeries()
        series.append(set1)
        series.append(set2)
        series.append(set3)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Количество выполненных типов задач")

        categories = [""]
        axisY = QBarCategoryAxis()
        axisY.append(categories)
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)
        axisX = QValueAxis()
        axisX.setLabelFormat("%d")
        axisX.setTickType(QValueAxis.TicksDynamic)
        axisX.setTickInterval(1)
        axisX.setMinorTickCount(0)
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        chart_view.setMinimumHeight(300)
        parent_layout.addWidget(chart_view)
