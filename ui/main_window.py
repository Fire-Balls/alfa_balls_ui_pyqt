# coding:utf-8
import sys
import os
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout,QLineEdit,
                               QTableWidget, QHeaderView, QTableWidgetItem,QVBoxLayout)
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, FluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont, InfoBadge,
                            InfoBadgePosition, FluentBackgroundTheme)
from qfluentwidgets import FluentIcon as FIF
from ui.kanban_desk.kanban_desk_table import HomeInterface

class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class Window(FluentWindow):
    ICON_PATH = os.path.join(os.path.dirname(__file__), 'resource', 'logo-alfabank.svg')
    print('Icon_path', ICON_PATH)
    def __init__(self):
        super().__init__()

    # def __init__(self):
    #     super().__init__()
    #     # create sub interface
        try:
            #super().__init__()
            print("Window: super().__init__() successful")
            try:
                # create sub interface
                self.homeInterface = HomeInterface(self)  # Используем новый класс
                print("Window: HomeInterface created")
                self.folderInterface = Widget('Folder Interface', self)
                print("Window: folderInterface created")
                self.settingInterface = Widget('Setting Interface', self)
                print("Window: settingInterface created")

                self.initNavigation()
                print("Window: initNavigation() successful")
                self.initWindow()
                print("Window: initWindow() successful")
            except Exception as e:
                print(f"Window: Error during initialization: {e}")
        except Exception as e:
            print(f"Window: Error during super().__init__(): {e}")

        # self.homeInterface = HomeInterface(self)  # Используем новый класс
        # self.folderInterface = Widget('Folder Interface', self)
        # self.settingInterface = Widget('Setting Interface', self)
        #
        # self.initNavigation()
        # self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.addSubInterface(self.folderInterface, FIF.FOLDER, 'Folder library', NavigationItemPosition.SCROLL)

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('zhiyiYo', 'resource/shoko.png'),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(900, 900)

        icon_size = QSize(100, 100)
        print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
        script_directory = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_directory, 'resource', 'logo-alfabank.svg')
        # icon_path = os.path.join(script_directory, 'resource\logo-alfabank.svg')
        print(f"Путь к иконке: {script_directory}")
        # icon = QIcon('resource/logo-alfabank.svg')
        # Проверяем, существует ли файл
        print(os.path.exists(r'D:\OneDrive\Документы\6сем\пп\desk\ui\resource\logo-alfabank.svg'))
        print(icon_path)
        if not os.path.exists(r'D:\OneDrive\Документы\6сем\пп\desk\ui\resource\logo-alfabank.svg'):#os.path.exists(icon_path):
            print(f"Ошибка: Файл иконки не найден по пути: {icon_path}")
            # Можно использовать иконку по умолчанию или выйти из программы
            icon = QIcon()  # Пустая иконка
        else:
            print(f"Файл иконки найден по пути: {icon_path}")
            icon = QIcon(icon_path)
        print('ddddddddddddd')
        pixmap = icon.pixmap(icon_size)
        scaled_icon = QIcon(pixmap)
        print('fffffffffffffwww')

        self.setWindowIcon(scaled_icon)
        self.setWindowTitle('Kanban Project')

        # self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        # self.setWindowTitle('PyQt-Fluent-Widgets')

        # desktop = QApplication.screens()[0].availableGeometry()
        # w, h = desktop.width(), desktop.height()
        # self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        #
        # # set the minimum window width that allows the navigation panel to be expanded
        # # self.navigationInterface.setMinimumExpandWidth(900)
        # # self.navigationInterface.expand(useAni=False)
        #
        # desktop = QApplication.screens()[0].availableGeometry()
        # w, h = desktop.width(), desktop.height()
        # self.move(w//2 - self.width()//2, h//2 - self.height()//2)


    def showMessageBox(self):
        w = MessageBox(
            'перейти на веб?',
            '',
            self
        )
        w.yesButton.setText('да')
        w.cancelButton.setText('нет')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://teamproject.urfu.ru/#/7387c03e-829a-4a1a-b635-f06fea3049bd/about"))


if __name__ == '__main__':
    #setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()