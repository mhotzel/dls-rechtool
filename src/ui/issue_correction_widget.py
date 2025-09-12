
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import date
import json
from typing import List
from PySide6.QtWidgets import (
    QWidget, QFrame, QGroupBox, QHeaderView,
    QTableView, QComboBox, QVBoxLayout, QGridLayout, QDateEdit, QLabel
)

from PySide6.QtCore import (
    Qt, QDate, Signal, QAbstractTableModel
)
from pydantic import BaseModel

from application.app_event import AppEvent, LogLevel
from application.event_dispatcher import EventDispatcher
from domain.find_inv_order_events_cmd import Document, FindInvoiceAndOrderEventsCmd
from services.event_store.event import Event
from services.event_store.eventstore import EventStore

SECTIONS_DOCS = {
    0: "Datum",
    1: "Typ",
    2: "Dok-Nr",
    3: 'Lief-Nr',
    4: 'Lieferant'
}


class DocumentModel(QAbstractTableModel):

    def __init__(self, parent, docs: List[Document]):
        super().__init__(parent)
        self.docs = docs

    def data(self, index, /, role=...):
        if role == Qt.ItemDataRole.DisplayRole:
            doc: Document = self.docs[index.row()]
            match index.column():
                case 0:
                    return QDate(doc.doc_date.year, doc.doc_date.month, doc.doc_date.day)
                case 1:
                    return doc.doc_type
                case 2:
                    return doc.doc_id
                case 3:
                    return doc.suppl_id
                case 4:
                    return doc.suppl_name

    def rowCount(self, /, parent=...):
        return len(self.docs)

    def columnCount(self, /, parent=...):
        return 5

    def headerData(self, section, orientation, /, role=...):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return SECTIONS_DOCS.get(section)


class SearchData(BaseModel):
    """Sammelt die Daten aus den Suchfeldern über Signale"""
    date_from: date = date.today()
    date_to: date = date.today()
    suppl_id: str | None = None
    issue_type: str | None = None

    def get_qdate_from(self) -> QDate:
        return QDate(self.date_from.year, self.date_from.month, self.date_from.day)

    def get_qdate_to(self) -> QDate:
        return QDate(self.date_to.year, self.date_to.month, self.date_to.day)

    def date_changed_from(self, qd: QDate) -> None:
        self.date_from = qd.toPython()

    def date_changed_to(self, qd: QDate) -> None:
        self.date_to = qd.toPython()

    def doctype_changed(self, issue_type: str) -> None:
        self.issue_type = issue_type

    def supplier_changed(self, supplier: str) -> None:
        self.suppl_id = supplier


class IssueCorrectionWidget(QGroupBox):
    """Dient der Korrektur von Rechnungen, Bestellbestätigungen usw."""

    docsSignal = Signal(list)
    errorSignal = Signal(str)

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evt_store: EventStore):
        super().__init__('Korrekturen durchführen', parent=parent)
        self.evt_dispatcher = event_dispatcher
        self.evt_store = evt_store
        self.search_params: SearchData = SearchData()
        self.executor = ThreadPoolExecutor(max_workers=2)

        self.docsSignal.connect(self.fill_table_model)
        self.errorSignal.connect(self.status_error)

        self.__build_ui()

    def status_error(self, msg: str):
        self.evt_dispatcher.send(
            AppEvent(evt_lvl=LogLevel.CRITICAL, evt_type='status-message', evt_data=msg))

    def __build_ui(self):
        """Baut die Oberfläche"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.head_widget = self._get_head()
        self.hitlist_widget = self._get_hitlist_widget()
        self.positions_widget = self._get_positions_widget()

        layout.addWidget(self.head_widget)
        layout.addWidget(self.hitlist_widget)
        layout.addWidget(self.positions_widget)

        #layout.addStretch(1)

    def _get_head(self) -> QWidget:
        """Baut den Kopf"""
        head = QFrame(self)
        layout = QGridLayout(head)
        head.setLayout(layout)

        self.lbl_doctype = QLabel('Dok.-Typ wählen')
        layout.addWidget(self.lbl_doctype, 0, 0)

        self.cmb_doctype = QComboBox(self, editable=False)
        self.__fill_doctypes(self.cmb_doctype)
        self.cmb_doctype.setMinimumContentsLength(20)
        layout.addWidget(self.cmb_doctype, 1, 0)

        self.lbl_suppler = QLabel('Lieferant wählen')
        layout.addWidget(self.lbl_suppler, 0, 1)

        self.cmb_supplier = QComboBox(self, editable=False)
        self.cmb_supplier.setMinimumContentsLength(20)
        layout.addWidget(self.cmb_supplier, 1, 1)

        self.lbl_date_from = QLabel('Beginn-Dtm')
        layout.addWidget(self.lbl_date_from, 0, 2)

        self.txt_issue_date_from = QDateEdit(
            self.search_params.get_qdate_from(), self)
        self.txt_issue_date_from.setCalendarPopup(True)
        self.txt_issue_date_from.setDisplayFormat("dd.MM.yyyy")
        self.txt_issue_date_from.setMinimumDate(QDate(2025, 1, 1))
        self.txt_issue_date_from.setMaximumDate(QDate.currentDate())
        layout.addWidget(self.txt_issue_date_from, 1, 2)

        self.lbl_date_from = QLabel('Ende-Dtm')
        layout.addWidget(self.lbl_date_from, 0, 3)

        self.txt_issue_date_to = QDateEdit(
            self.search_params.get_qdate_to(), self)
        self.txt_issue_date_to.setCalendarPopup(True)
        self.txt_issue_date_to.setDisplayFormat("dd.MM.yyyy")
        self.txt_issue_date_to.setMinimumDate(QDate(2025, 1, 1))
        self.txt_issue_date_to.setMaximumDate(QDate.currentDate())
        layout.addWidget(self.txt_issue_date_to, 1, 3)
        layout.setColumnStretch(4, 1)

        self.txt_issue_date_from.dateChanged.connect(
            lambda evt: self.search_data_changed())
        self.txt_issue_date_to.dateChanged.connect(
            lambda evt: self.search_data_changed())

        self.cmb_doctype.currentIndexChanged.connect(
            lambda evt: self.search_data_changed())

        self.cmb_supplier.currentIndexChanged.connect(
            lambda evt: self.search_data_changed())

        return head

    def _get_hitlist_widget(self) -> QWidget:
        """Baut die Trefferliste"""
        hitlist_frame = QGroupBox('Trefferliste', self)
        layout = QVBoxLayout(hitlist_frame)
        hitlist_frame.setLayout(layout)
        self.hitlist_view = QTableView(
            hitlist_frame, showGrid=True, cornerButtonEnabled=True)

        self.hitlist_view.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows)
        header = self.hitlist_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.hitlist_view, stretch=1)
        return hitlist_frame

    def _get_positions_widget(self) -> QWidget:
        """Baut die Trefferliste"""
        positions_frame = QGroupBox('Positionen', self)
        layout = QGridLayout(positions_frame)
        positions_frame.setLayout(layout)
        self.poslist_view = QTableView(
            positions_frame, showGrid=True, cornerButtonEnabled=True)
        self.poslist_view.setMinimumHeight(200)
        self.poslist_view.setMaximumHeight(500)
        layout.addWidget(self.poslist_view)

        return positions_frame

    def search_data_changed(self) -> None:
        """Kümmert sich um die Suche, wenn sich Suchparameter geändert haben"""
        self.search_params.date_from = self.txt_issue_date_from.date().toPython()
        self.search_params.date_to = self.txt_issue_date_to.date().toPython()
        self.search_params.suppl_id = self.cmb_supplier.currentData()
        self.search_params.issue_type = self.cmb_doctype.currentData()

        cmd = FindInvoiceAndOrderEventsCmd(
            date_from=self.search_params.date_from,
            date_to=self.search_params.date_to,
            suppl_id=self.search_params.suppl_id,
            issue_id=self.search_params.issue_type,
            evt_store=self.evt_store
        )

        def fetch_docs(cmd: FindInvoiceAndOrderEventsCmd):
            """Holt die Daten aus dem EventStore - in einem eigenen Thread"""

            docs: List[Document] = cmd.findAll()
            return docs

        def on_fetch_docs_done(fut: Future[List[Document]]):
            """Callback, wenn das Lesen fertig ist"""

            try:
                docs: List[Document] = fut.result()
                self.docsSignal.emit(docs)
            except Exception as e:
                self.errorSignal.emit(f"Fehler beim Abruf der Daten: '{e}'")

        future = self.executor.submit(fetch_docs, cmd)
        future.add_done_callback(on_fetch_docs_done)

    def fill_table_model(self, docs: List[Document]):
        """Erzeugt ein Table Model und setzt es in die TableView"""
        tableModel = DocumentModel(self, docs=docs)
        self.hitlist_view.setModel(tableModel)

    def __fill_doctypes(self, cmbBox: QComboBox) -> None:
        """Füllt die Typen-ComboBox"""
        cmbBox.addItem('<Typ wählen>', None)
        cmbBox.addItem('Rechnung', 'invoice')
        cmbBox.addItem('Bestellung', 'order')
        cmbBox.addItem('Bestellbestätigung', 'order_confirmation')

    def showEvent(self, event):
        self.__fill_suppliers(self.cmb_supplier)
        return super().showEvent(event)

    def __fill_suppliers(self, cmbBox: QComboBox) -> None:
        """Füllt die Lieferanten-ComboBox"""
        evts = self.evt_store.readEventsByType('supplier.onboarded')

        cmbBox.addItem('<Lieferant wählen>', None)
        for evt in evts:
            data = json.loads(evt.data)
            cmbBox.addItem(data['suppl_name'], data['suppl_id'])

        return None
