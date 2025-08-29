import sys

from services.event_store.sqlite_eventstore import SqliteEventStore
from services.config_service import ConfigService
from PySide6.QtWidgets import QApplication
from ui.setup_window import SetupWindow
from ui.main_window import MainWindow

from application.event_dispatcher import EventDispatcherImpl


class ApplicationContext:
    """Application context für das DLS Rechnungstool. Stellt alle benötigten zentralen Services bereit."""

    def __init__(self):
        self.qApp = QApplication(sys.argv)
        self.qApp.setStyle('Fusion')
        # print(QStyleFactory.keys())
        self.__event_store = SqliteEventStore()
        self.dbfile: str = None
        self.event_dispatcher = EventDispatcherImpl()
        self.config_service = ConfigService()

        self.setup_window = SetupWindow(self.config_service)
        self.event_dispatcher.register('start-config-db', self.setup_window.processEvent)
        self.event_dispatcher.register('app-quit', lambda e: self.quit())

    def quit(self) -> None:
        """Beendet die Anwendung ordnungsgemäß"""
        self.event_store.close()
        self.qApp.exit(0)

    @property
    def event_store(self):
        """Returns the event store instance."""
        if self.__event_store is None and self.config_service.getDatabaseFilePath():
            self.__event_store = SqliteEventStore(self.dbfile)

        return self.__event_store

    def run(self) -> None:
        """Startet die Anwendung"""
        dbfile = self.config_service.getDatabaseFilePath()
        if not dbfile:
            self.setup_window.show()
            self.qApp.exec()

        dbfile = self.config_service.getDatabaseFilePath()
        if dbfile:
            self.event_store.dbFile = str(dbfile)
            self.mainWindow = MainWindow(self.event_dispatcher, self.event_store)
            self.mainWindow.show()
            self.qApp.exec()
