# coding:utf-8
import sys

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

    def __init__(self):
        super().__init__()
        # create sub interface
        self.homeInterface = HomeInterface(self)  # Используем новый класс
        self.folderInterface = Widget('Folder Interface', self)
        self.settingInterface = Widget('Setting Interface', self)

        self.initNavigation()
        self.initWindow()

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
        icon = QIcon('../logo-alfabank.svg')
        pixmap = icon.pixmap(icon_size)
        scaled_icon = QIcon(pixmap)

        self.setWindowIcon(scaled_icon)
        self.setWindowTitle('Kanban Project')

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)


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