from PySide6.QtWidgets import QStackedWidget
from application.app_event import AppEvent
from services.event_store.eventstore import EventStore
from ui.edeka_orderconf_widget import EdekaOrderConfirmationImportWidget
from ui.empty_widget import EmptyPane
from ui.import_xinvoice_widget import ImportEInvoice
from ui.manual_position_editor_widget import ManualPositionEditorWidget
from ui.paxan_orderconf_widget import PaxanOrderConfirmationImportWidget
from ui.suppliers_editor import SuppliersEditorWidget
from application.event_dispatcher import EventDispatcher


class MainPart(QStackedWidget):
    def __init__(self, parent, event_dispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__(parent)
        self.event_dispatcher: EventDispatcher = event_dispatcher
        self.evtStore: EventStore = evtStore
        self._build_ui()
        self.event_dispatcher.register('import-invoice', self.process_event)
        self.event_dispatcher.register('edit-suppliers', self.process_event)
        self.event_dispatcher.register('import-manual-positions', self.process_event)
        self.event_dispatcher.register(
            'import-edeka-orderconfirmation', self.process_event)
        self.event_dispatcher.register(
            'import-paxan-orderconfirmation', self.process_event)

        self.event_mapping = {
            'import-invoice': self.invoiceWidget,
            'edit-suppliers': self.suppliersEditor,
            'import-edeka-orderconfirmation': self.edeka_orderconf_widget,
            'import-paxan-orderconfirmation': self.paxan_orderconf_widget,
            'import-manual-positions': self.manual_positions_widget
        }

    def _build_ui(self):

        self.emptyWidget = EmptyPane(self)
        self.addWidget(self.emptyWidget)

        self.invoiceWidget = ImportEInvoice(
            self, self.event_dispatcher, self.evtStore)
        self.addWidget(self.invoiceWidget)

        self.suppliersEditor = SuppliersEditorWidget(
            self, self.event_dispatcher, self.evtStore)
        self.addWidget(self.suppliersEditor)

        self.edeka_orderconf_widget = EdekaOrderConfirmationImportWidget(
            self, self.event_dispatcher, self.evtStore)
        self.addWidget(self.edeka_orderconf_widget)

        self.paxan_orderconf_widget = PaxanOrderConfirmationImportWidget(
            self, self.event_dispatcher, self.evtStore)
        self.addWidget(self.paxan_orderconf_widget)

        self.manual_positions_widget = ManualPositionEditorWidget(
            self, self.event_dispatcher, self.evtStore)
        self.addWidget(self.manual_positions_widget)

        self.setCurrentWidget(self.emptyWidget)

    def process_event(self, event: AppEvent) -> None:
        """Verarbeitet ein Event"""
        self.setCurrentWidget(self.event_mapping[event.evt_type])
