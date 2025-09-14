
from pathlib import Path
from PySide6.QtWidgets import (
    QGroupBox, QWidget, QFrame, QVBoxLayout,
    QPushButton, QLineEdit, QGridLayout,
    QFileDialog, QLabel
)

import locale

from application.app_event import AppEvent, LogLevel
from application.event_dispatcher import EventDispatcher
from domain.paxan_order_confirm_import_cmd import PaxanOrderConfirmationImportCmd
from services.event_store.eventstore import EventStore
from services.readmodels.base_data_store import DataStore


class PaxanOrderConfirmationImportWidget(QGroupBox):

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evtStore: EventStore, dataStore: DataStore):
        super().__init__('Paxan-Bestellbestätigungen importieren', parent)
        locale.setlocale(locale.LC_ALL, '')
        self.evtStore = evtStore
        self.dataStore = dataStore
        self.suppl_id = '35'
        self.suppl_name = 'Paxan'
        self.evt_dispatcher = event_dispatcher
        self.__build_ui()

    def __build_ui(self) -> None:
        """Baut die Oberfläche"""
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.import_frame = QFrame(self)
        layout.addWidget(self.import_frame)
        layout.addStretch(1)

        self.import_frame.setLayout(QGridLayout(self.import_frame))
        self.btn_select_file = QPushButton(
            'Datei auswählen', parent=self.import_frame)

        txt = "ACHTUNG: Die Bestellbetätigungen werden "
        txt += f"'hart' der Lieferantennummer '{self.suppl_id}' zugeordnet!\n"
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
            evt = PaxanOrderConfirmationImportCmd(
                filename=self.txt_selected_file.text(),
                suppl_id=self.suppl_id,
                suppl_name=self.suppl_name
            ).createEvent()

            docs = self.dataStore.get_doc_list()
            for doc in docs:
                if doc.subject == evt.subject:
                    raise ValueError(f"Das Dokument '{evt.subject}' wurde bereits eingelesen")

            self.evtStore.add_event(evt, expected_version=None)
            self.evt_dispatcher.send(
                AppEvent(
                    evt_lvl=LogLevel.INFO,
                    evt_type='status-message',
                    evt_data='INFO:Die Bestellbestätigungen wurden importiert'
                )
            )

        except Exception as e:
            self.evt_dispatcher.send(
                AppEvent(
                    evt_lvl=LogLevel.CRITICAL,
                    evt_type='status-message',
                    evt_data=f"Import schlug fehl: {e}"
                )
            )

    def getFloat(self, data: str) -> float:
        data = data.replace('.', '')
        data = data.replace(',', '.')
        return float(data)
