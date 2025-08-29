from PySide6.QtWidgets import QStackedWidget
from application.app_event import AppEvent
from ui.empty_widget import EmptyPane
from ui.import_xinvoice import ImportEInvoice
from ui.suppliers_editor import SuppliersEditorWidget
from application.event_dispatcher import EventDispatcher


class MainPart(QStackedWidget):
    def __init__(self, parent, event_dispatcher: EventDispatcher):
        super().__init__(parent)
        self.event_dispatcher = event_dispatcher
        self._build_ui()
        self.event_dispatcher.register('import-invoice', self.process_event)
        self.event_dispatcher.register('edit-suppliers', self.process_event)

        self.event_mapping = {
            'import-invoice': self.invoiceWidget,
            'edit-suppliers': self.suppliersEditor
        }

    def _build_ui(self):

        self.emptyWidget = EmptyPane(self)
        self.addWidget(self.emptyWidget)

        self.invoiceWidget = ImportEInvoice(self)
        self.addWidget(self.invoiceWidget)

        self.suppliersEditor = SuppliersEditorWidget(self)
        self.addWidget(self.suppliersEditor)
        self.setCurrentWidget(self.emptyWidget)

    def process_event(self, event: AppEvent) -> None:
            """Verarbeitet ein Event"""
            self.setCurrentWidget(self.event_mapping[event.evt_type])

