from os import path
import json
from pathlib import PurePath
import sys
import uuid
from PySide6.QtWidgets import QMainWindow, QApplication, QMenu, QWidget, QHBoxLayout, QPushButton, QSizePolicy
from PySide6.QtGui import QIcon, QScreen, QAction, QKeySequence
from PySide6.QtCore import QSize
from application.application_context import ApplicationContext
from ui.leftbar import LeftBar
from ui.mainpart import MainPart
from api.eventstore import Event
from api.sqlite_eventstore import SqliteEventStore
from domain.fakturx_invoice import FakturXInvoice


class MainWindow(QMainWindow):

    def __init__(self, app: QApplication, appContext: ApplicationContext):
        super().__init__()
        self.app = app
        self.appContext = appContext
        self.setWindowTitle("DLS - Preise und Mengen")
        self._buildGui()
        self._addMenus()

    def _addMenus(self):
        fileMenu = QMenu("Datei", self)
        fileMenu.setToolTipsVisible(True)
        quitAction = QAction("Beenden", self, toolTip="Beenden",
                             shortcut=QKeySequence("alt+f4"))
        quitAction.triggered.connect(self.app.quit)
        fileMenu.addAction(quitAction)
        self.menuBar().addMenu(fileMenu)

    def _buildGui(self):
        self.setStyleSheet("""
            QWidget { background: #f3f3f3; }
            QPushButton { padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px; background-color: rgb(142,190,68); font-weight: bold; color: white; }
            QPushButton:hover { background: #eaeaea; color: black; }
            QFrame {border: 1px solid; border-radius: 5px; background-color: white;}
        """)

        _centralWidget = QWidget()
        self.setCentralWidget(_centralWidget)

        _leftBar = LeftBar(_centralWidget, self.appContext)
        _rightBar = MainPart(_centralWidget, self.appContext)

        _leftBar.setSizePolicy(QSizePolicy.Policy.Fixed,
                               QSizePolicy.Policy.Expanding)
        _rightBar.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        _layout = QHBoxLayout(_centralWidget)
        _layout.addWidget(_leftBar)
        _layout.addWidget(_rightBar)
        _centralWidget.setLayout(_layout)

    def show(self):
        super().show()
        screenSize = QScreen.availableGeometry(QApplication.primaryScreen())
        winXpos = ((screenSize.width() - self.width())/2)
        winYpos = ((screenSize.height() - self.height())/2)
        self.move(winXpos, winYpos)


def _createIcons():
    my_icon = QIcon()
    my_icon.addFile(path.join('assets', 'favicon16x16.jpg'), QSize(16, 16))
    my_icon.addFile(path.join('assets', 'favicon24x24.jpg'), QSize(24, 24))
    my_icon.addFile(path.join('assets', 'favicon32x32.jpg'), QSize(32, 32))
    my_icon.addFile(path.join('assets', 'favicon48x48.jpg'), QSize(48, 48))
    my_icon.addFile(path.join('assets', 'favicon64x64.jpg'), QSize(64, 64))
    my_icon.addFile(path.join('assets', 'favicon256x256.jpg'), QSize(256, 256))
    return my_icon


def main():
    appContext = ApplicationContext()
    appContext.event_store
    app = QApplication(sys.argv)
    app.setWindowIcon(_createIcons())
    mw = MainWindow(app=app, appContext=appContext)
    mw.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()