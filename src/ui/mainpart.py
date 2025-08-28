from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy, QFrame, QStackedWidget
from ui.import_xinvoice import ImportEInvoice
from application.event_dispatcher import EventDispatcher

class MainPart(QStackedWidget):
    def __init__(self, parent, event_dispatcher: EventDispatcher):
        super().__init__(parent)
        self.event_dispatcher = event_dispatcher
        self._build_ui()

    def _build_ui(self):
        self.invoiceWidget = ImportEInvoice(self)
        self.addWidget(self.invoiceWidget)
