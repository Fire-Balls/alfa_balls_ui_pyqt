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
        self.setWindowTitle("Аналитика")
        self.resize(800, 600)
        self.setMinimumSize(500, 400)

        self.project_id = project_id

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
        self.add_metrics_section(self.scroll_layout)
        self.add_chart_placeholder(self.scroll_layout)
        self.add_horizontal_bar_chart(self.scroll_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics_section)
        self.timer.start(6000)  # 60 000 мс = 60 секунд

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
        # Очистить старые блоки
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
        # Пример данных: имя участника → количество решённых задач
        # todo нужно считать кол-во задач данного пользователя в статусе DONE
        project_data = {
            "Анна": 7,
            "Иван": 5,
            "Мария": 15,
            "Олег": 3,"Олег1": 23,"Олег8": 1,"Олег9": 14,"Олег10": 4,
            "Елена": 6
        }

        # Создаём набор столбцов
        bar_set = QBarSet("Выполненные задачи")
        bar_set.append(list(project_data.values()))

        # Добавляем в серию
        series = QBarSeries()
        series.append(bar_set)

        # Создаём график
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Количество выполненных задач по участникам")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # Ось X — участники
        axis_x = QBarCategoryAxis()
        names = list(project_data.keys())
        axis_x.append(names)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        # Ось Y — количество задач
        axis_y = QValueAxis()
        axis_y.setTitleText("Задачи")
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        # Создаём виджет
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.renderHints().Antialiasing)
        chart_view.setMinimumHeight(300)

        parent_layout.addWidget(chart_view)

        def on_bar_clicked(index):
            name = names[index]
            value = bar_set.at(index)

            bar_pos = chart.mapToPosition(QPointF(index, value), series)
            global_pos = chart_view.mapToGlobal(chart_view.mapFromScene(bar_pos))

            QToolTip.showText(global_pos, f"<b>{name}</b><br>Задач: {int(value)}", chart_view)

        bar_set.clicked.connect(on_bar_clicked)

    def add_horizontal_bar_chart(self, parent_layout):
        # Тестовые значения:
        total_duration = 120  # Общее время выполнения задач
        team_time = 140  # Время, потраченное командой

        set1 = QBarSet("Время выполнения задач")
        set2 = QBarSet("Время работы команды")

        set1 << total_duration
        set2 << team_time

        series = QHorizontalBarSeries()
        series.append(set1)
        series.append(set2)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Сравнение времени выполнения задач и работы команды в часах")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        categories = [""]
        axisY = QBarCategoryAxis()
        axisY.append(categories)
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)
        axisX = QValueAxis()
        axisX.setRange(0, max(total_duration, team_time) + 5)
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        chart_view.setMinimumHeight(300)
        parent_layout.addWidget(chart_view)
