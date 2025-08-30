from pathlib import Path
from typing import List
import uuid
from PySide6.QtWidgets import (
    QGroupBox, QWidget, QFrame, QVBoxLayout,
    QPushButton, QLineEdit, QGridLayout,
    QFileDialog
)

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from application.app_event import AppEvent
from application.event_dispatcher import EventDispatcher
from domain.order_item import OrderItem
from services.event_store.eventstore import EventStore, Event
from ui.status_msg_widget import StatusMessageWidget


class EdekaOrderConfirmationImportWidget(QGroupBox):

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__('EDEKA-Bestellbestätigungen importieren', parent)
        self.evtStore = evtStore
        self.evt_dispatcher = event_dispatcher
        self.__build_ui()

    def __build_ui(self) -> None:
        """Baut die Oberfläche"""
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.import_frame = QFrame(self)
        layout.addWidget(self.import_frame)
        layout.addStretch(1)
        self.statusWidget = StatusMessageWidget(self, self.evt_dispatcher)
        layout.addWidget(self.statusWidget)

        self.import_frame.setLayout(QGridLayout(self.import_frame))
        self.btn_select_file = QPushButton(
            'Datei auswählen', parent=self.import_frame)

        self.btn_select_file.clicked.connect(lambda evt: self.select_file())
        self.txt_selected_file = QLineEdit(
            '', parent=self.import_frame, readOnly=True)

        self.btn_start_import = QPushButton(
            'Import starten', parent=self.import_frame)
        self.btn_start_import.clicked.connect(lambda evt: self.start_import())
        self.btn_start_import.setEnabled(False)

        self.import_frame.layout().addWidget(self.btn_select_file, 0, 0)
        self.import_frame.layout().addWidget(self.txt_selected_file, 1, 0)
        self.import_frame.layout().addWidget(self.btn_start_import, 2, 0)

    def select_file(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            caption='Bestellbestätigungsdatei auswählen',
            filter="Bestellungen-Datei (*.xlsx)"
        )

        if filename:
            self.txt_selected_file.setText(str(Path(filename)))
            self.btn_start_import.setEnabled(True)

    def start_import(self):
        wb: Workbook = load_workbook(
            filename=self.txt_selected_file.text(),
            read_only=True, data_only=True)
        ws: Worksheet = wb.worksheets[0]
        item: OrderItem = None
        try:
            for row in ws.iter_rows(3, min_col=1, max_col=11, values_only=True):
                if row[2] is None:
                    break
                item = OrderItem(
                    idx=row[0],
                    seller_id='1',
                    order_confirm=row[1],
                    pos_seller_id=row[2],
                    pos_global_id=row[3],
                    pos_name=row[4],
                    pos_quantity=row[5],
                    pos_unitcode=row[6],
                    pos_packaging_quantity=row[7],
                    pos_order_date=row[8].date(),
                    pos_price=row[9],
                    pos_total_line_amount=row[10]
                )
                evt = Event.createEvent(
                    id=uuid.uuid1(),
                    subject=f'orderconfirmation-{item.order_confirm}-{item.idx}',
                    type='orderitem.imported',
                    data=item.model_dump_json()
                )
                self.evtStore.add_event(evt=evt, expected_version=-1)
                self.evt_dispatcher.send(AppEvent(
                    evt_type='status-message', evt_data=f"INFO:Bestellbestätig '{item.idx}' wurden importiert"))
                
            self.evt_dispatcher.send(AppEvent(
                evt_type='status-message', evt_data='INFO:Die Bestellbestätigungen wurden importiert'))
        except Exception as e:
            self.evt_dispatcher.send(AppEvent(
                evt_type='status-message', evt_data=f"CRITICAL:Import war fehlerhaft bei '{item}': {e}"))
