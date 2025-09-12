from contextlib import closing
from importlib.resources import files, as_file
from os import path
import os
from pathlib import Path
from queue import Empty, SimpleQueue
from application.app_event import AppEvent
from services.event_store.eventstore import EventStore
from services.readmodels.base_data_store import DataStore
from services.thread_worker import Status
from ui.leftbar import LeftBar
from ui.mainpart import MainPart

from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QAction, QKeySequence, QScreen, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QSizePolicy, QWidget, QGridLayout

from application.event_dispatcher import EventDispatcher
from ui.status_msg_widget import StatusMessageWidget

class MainWindow(QMainWindow):

    def __init__(self, eventDispatcher: EventDispatcher, evtStore: EventStore, dataStore: DataStore, status_queue: SimpleQueue):
        super().__init__()
        self.evtStore = evtStore
        self.setWindowTitle("DLS - Rechnungs- und Lieferantendatenerfassung")
        self.event_dispatcher: EventDispatcher = eventDispatcher
        self.evtStore: EventStore = evtStore
        self.dataStore = dataStore
        self.status_queue = status_queue
        self._buildGui()
        self._addMenus()
        self.setWindowIcon(self._createIcons())
        self.timer = QTimer(self, interval=2000)
        self.timer.timeout.connect(self.update_status)
        self.timer.start()

    def update_status(self):
        """Updated die Status-Message"""
        try:
            msg: Status = self.status_queue.get(block=False)
            self.event_dispatcher.send(AppEvent(evt_type='status-message', evt_data=msg.payload))
        except Empty:
            pass


    def _createIcons(self):
        my_icon = QIcon()
        my_icon.addFile(str(files('assets') / 'favicon16x16.jpg'), QSize(16, 16))
        my_icon.addFile(str(files('assets') / 'favicon24x24.jpg'), QSize(24, 24))
        my_icon.addFile(str(files('assets') / 'favicon32x32.jpg'), QSize(32, 32))
        my_icon.addFile(str(files('assets') / 'favicon48x48.jpg'), QSize(48, 48))
        my_icon.addFile(str(files('assets') / 'favicon64x64.jpg'), QSize(64, 64))
        my_icon.addFile(str(files('assets') / 'favicon256x256.jpg'), QSize(256, 256))
        return my_icon

    def _addMenus(self):
        fileMenu = QMenu("Datei", self)
        fileMenu.setToolTipsVisible(True)
        quitAction = QAction("Beenden", self, toolTip="Beenden",
                             shortcut=QKeySequence("alt+f4"))
        #quitAction.triggered.connect(self.close)
        quitAction.triggered.connect(lambda e: self.event_dispatcher.send(AppEvent(evt_type='app-quit')))
        fileMenu.addAction(quitAction)
        self.menuBar().addMenu(fileMenu)

    def closeEvent(self, event):
        self.event_dispatcher.send(AppEvent(evt_type='app-quit'))
        return super().closeEvent(event)

    def readStyleSheet(self) -> str:
        """liest das StyleSheet als String ein"""
        return files("ui").joinpath("stylesheet.css").read_text(encoding="utf-8")

    def _buildGui(self):
        _centralWidget = QWidget()
        _centralWidget.setObjectName("centralWidget")

        self.setStyleSheet(self.readStyleSheet())

        self.setCentralWidget(_centralWidget)
        self.leftBar = LeftBar(_centralWidget, self.event_dispatcher)
        self.main_part = MainPart(_centralWidget, self.event_dispatcher, self.evtStore, self.dataStore)
        self.status_widget = StatusMessageWidget(_centralWidget, self.event_dispatcher)

        self.leftBar.setSizePolicy(QSizePolicy.Policy.Fixed,
                               QSizePolicy.Policy.Expanding)
        self.main_part.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        _inner_layout = QGridLayout(_centralWidget)
        _inner_layout.addWidget(self.leftBar, 0, 0)
        _inner_layout.addWidget(self.main_part, 0, 1)
        _inner_layout.addWidget(self.status_widget, 1, 0, 1, 2)
        _centralWidget.setLayout(_inner_layout)

    def show(self):
        super().show()
        screenSize = QScreen.availableGeometry(QApplication.primaryScreen())
        winXpos = ((screenSize.width() - self.width())/2)
        winYpos = ((screenSize.height() - self.height())/2)
        self.move(winXpos, winYpos)
