import sys
from typing import MutableMapping
from application.config_service_listener import ConfigServiceListener
from application.invoice_import_listener import InvoiceImportListener
from services.sqlite_eventstore import SqliteEventStore
from services.config_service import ConfigService
from PySide6.QtWidgets import QApplication
from ui.setup_window import SetupWindow
from ui.main_window import MainWindow

from application.event_dispatcher import EventDispatcher, EventDispatcherImpl, Listener


class ApplicationContext:
    """Application context für das DLS Rechnungstool. Stellt alle benötigten zentralen Services bereit."""

    def __init__(self):
        self.qApp = QApplication(sys.argv)
        self.__event_store = None
        self.dbfile: str = None
        self.event_dispatcher = EventDispatcherImpl()
        self.config_service = ConfigService()

        self.__registerServices()
        self.__registerListeners()
        self.__register_widgets()

    def __registerServices(self):
        self.config_service = ConfigService()
       

    def __registerListeners(self):
        setupWindow = SetupWindow(self.config_service, firstStart=False)
        self.event_dispatcher.register(
            'config-db', ConfigServiceListener(setupWin=setupWindow))
        self.event_dispatcher.register(
            'import-invoice', InvoiceImportListener()
        )

    def __register_widgets(self):
        self.mainWindow = MainWindow(self.event_dispatcher)
        self.setup_window = SetupWindow(self.config_service)

    @property
    def event_store(self):
        """Returns the event store instance."""
        if self.__event_store is None and self.config_service.getDatabaseFilePath():
            self.__event_store = SqliteEventStore(self.dbfile)

        return self.__event_store

    def run(self) -> None:
        """Startet die Anwendung"""
        if not self.config_service.getDatabaseFilePath():
            self.setup_window.show()
            self.qApp.exec()

        if self.config_service.getDatabaseFilePath():
            mainWindow = MainWindow(self.event_dispatcher)
            mainWindow.show()
            self.qApp.exec()
