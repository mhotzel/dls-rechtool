from queue import Empty
import sys

from application import db_migration
from application.app_event import AppEvent, LogLevel
from services.read_model_worker import ReadModelWorker
from services.thread_worker import Status
from services.event_store.sqlite_eventstore import SqliteEventStore, SqliteConnectionManager
from services.config_service import ConfigService
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui.setup_window import SetupWindow
from ui.main_window import MainWindow

from application.event_dispatcher import EventDispatcherImpl


class ApplicationContext:
    """Application context für das DLS Rechnungstool. Stellt alle benötigten zentralen Services bereit."""

    def __init__(self):
        self.qApp = QApplication(sys.argv)
        self.qApp.setStyle('Fusion')
        # print(QStyleFactory.keys())
        self.conn_manager = SqliteConnectionManager()
        self.event_store = SqliteEventStore(self.conn_manager)
        self.dbfile: str = None
        self.event_dispatcher = EventDispatcherImpl()
        self.config_service = ConfigService()

        self.setup_window = SetupWindow(self.config_service)
        self.event_dispatcher.register(
            'start-config-db', self.setup_window.processEvent)
        self.event_dispatcher.register('app-quit', lambda e: self.quit())

        self.read_model_worker = ReadModelWorker(self.conn_manager)

    def quit(self) -> None:
        """Beendet die Anwendung ordnungsgemäß"""
        self.conn_manager.close_all_connections()
        self.read_model_worker.stop()
        self.qApp.exit(0)

    def run(self) -> None:
        """Startet die Anwendung"""
        dbfile = self.config_service.getDatabaseFilePath()
        if not dbfile:
            self.setup_window.show()
            self.qApp.exec()

        dbfile = self.config_service.getDatabaseFilePath()
        if dbfile:
            self.conn_manager.dbFile = str(dbfile)
            db_migration.initial_setup(self.conn_manager.get_connection())
            # self.read_model_worker.start()

            self.mainWindow = MainWindow(
                self.event_dispatcher, self.event_store)

            self.mainWindow.show()
            self.qApp.exec()

