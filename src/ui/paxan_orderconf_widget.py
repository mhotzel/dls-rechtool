
from contextlib import closing
from datetime import date, datetime
from pathlib import Path
import re
import uuid
from PySide6.QtWidgets import (
    QGroupBox, QWidget, QFrame, QVBoxLayout,
    QPushButton, QLineEdit, QGridLayout,
    QFileDialog, QLabel
)

from csv import DictReader

import locale

from application.app_event import AppEvent
from application.event_dispatcher import EventDispatcher
from domain.order_confirmation import OrderConfirmation, OrderItem
from services.event_store.eventstore import EventStore
from services.event_store.event import Event
from ui.status_msg_widget import StatusMessageWidget


class PaxanOrderConfirmationImportWidget(QGroupBox):

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__('Paxan-Bestellbestätigungen importieren', parent)
        locale.setlocale(locale.LC_ALL, '')
        self.evtStore = evtStore
        self.seller_id = '35'
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

        txt = "ACHTUNG: Die Bestellbetätigungen werden "
        txt += f"'hart' der Lieferantennummer '{self.seller_id}' zugeordnet!\n"
        txt += "Paxan muss also in der Anwendung mit genau dieser Nummer angelegt sein"
        self.lbl_hinweis_liefnr = QLabel(txt, self.import_frame)
        self.lbl_hinweis_liefnr.setStyleSheet(
            '.QLabel {font-weight: bold; color: #CE0538}')

        self.btn_select_file.clicked.connect(lambda evt: self.select_file())
        self.txt_selected_file = QLineEdit(
            '', parent=self.import_frame, readOnly=True)

        self.btn_start_import = QPushButton(
            'Import starten', parent=self.import_frame)
        self.btn_start_import.clicked.connect(lambda evt: self.start_import())
        self.btn_start_import.setEnabled(False)

        self.import_frame.layout().addWidget(self.lbl_hinweis_liefnr, 0, 0)
        self.import_frame.layout().addWidget(self.btn_select_file, 1, 0)
        self.import_frame.layout().addWidget(self.txt_selected_file, 2, 0)
        self.import_frame.layout().addWidget(self.btn_start_import, 3, 0)

    def select_file(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            caption='Bestellbestätigungsdatei auswählen',
            filter="Bestellungen-Datei (*.csv)"
        )

        if filename:
            self.txt_selected_file.setText(str(Path(filename)))
            self.btn_start_import.setEnabled(True)

    def start_import(self):
        try:
            filename = self.txt_selected_file.text()
            match = re.search(r"(\d{8}-\d{6})", filename)
            if match:
                order_id = match.group(1)  # 20250826-173018
            else:
                raise LookupError(
                    f"Es konnte keine Bestell-ID aus dem Dateinamen '{filename}' extrahiert werden.")
            item = None
            with closing(open(filename, encoding='utf8')) as csv_file:
                reader = DictReader(csv_file)
                order_conf = OrderConfirmation(
                    seller_id=self.seller_id,
                    order_confirm=order_id,
                    # erstmal ein Dummy, wird mit der ersten Position gefixt
                    order_date=datetime.now().date()
                )
                for row in reader:
                    position = row['Position']
                    order_date = datetime.strptime(
                        row['Datum'], '%d.%m.%Y').date()
                    seller_assigned_id = row['ArtNr']
                    global_id = row['EAN']
                    name = row['Regaltext']
                    quantity = self.getFloat(row['Anzahl'])

                    price = self.getFloat(row['Preis'])
                    order_conf.order_date = order_date

                    item = OrderItem(
                        idx=position,
                        seller_assigned_id=seller_assigned_id,
                        global_id=global_id,
                        name=name,
                        quantity=quantity,
                        price=price
                    )
                    order_conf.positions.append(item)

            subject = f'orderconfirmation-{order_conf.order_confirm}'
            evt = Event.createEvent(
                uuid.uuid1(),
                subject=subject,
                type='order.imported',
                data=order_conf.model_dump_json()
            )
            self.evtStore.add_event(evt, expected_version=-1)
            self.evt_dispatcher.send(
                AppEvent(
                    evt_type='status-message', evt_data='INFO:Die Bestellbestätigungen wurden importiert'
                )
            )
            
        except Exception as e:
            self.evt_dispatcher.send(
                AppEvent(
                    evt_type='status-message', evt_data=f"CRITICAL:Import war fehlerhaft bei '{item}': {e}"
                )
            )

    def getFloat(self, data: str) -> float:
        data = data.replace('.', '')
        data = data.replace(',', '.')
        return float(data)
