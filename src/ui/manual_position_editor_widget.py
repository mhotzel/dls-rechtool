from typing import List, MutableMapping, Tuple
import uuid
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QGroupBox, QFrame, QLineEdit, QMessageBox, QHBoxLayout,
    QGridLayout, QLabel, QComboBox, QDateEdit, QHeaderView, QTableView, QMenu
)

from PySide6.QtGui import QIntValidator, QDoubleValidator, QAction
from PySide6.QtCore import Qt, QDate, QAbstractTableModel, QModelIndex, QLocale, QPoint


from application.app_event import AppEvent
from application.event_dispatcher import EventDispatcher
from domain.supplier_reader import SupplierReader
from domain.suppliers import Supplier
from services.event_store.eventstore import EventStore
from services.event_store.event import Event
from ui.status_msg_widget import StatusMessageWidget

import locale


class PositionTableModel(QAbstractTableModel):

    def __init__(self, /, parent=...):
        super().__init__(parent)
        locale.setlocale(locale.LC_ALL, '')
        self._data: List[Tuple[int, str, str, str, float]] = []

        self.posMapping: MutableMapping[int, Tuple[str, str]] = {
            0: ('Lfd.Nr', 'Laufende Nummer der Position', Qt.AlignmentFlag.AlignCenter),
            1: ('Artikel-Nr', 'Artikelnummer des Lieferanten', Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            2: ('GTIN', 'EAN / Strichcode', Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            3: ('Bezeichnung', 'Bezeichnung', Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            4: ('Einzelpreis', 'Einzelpreis (Netto)', Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        }

    def addPosition(self, idx: int, art_nr: str, gtin: str, name: str, price: str) -> None:
        """Fuegt dem Modell eine Zeile hinzu"""
        self._data.append((idx, art_nr, gtin, name, price))
        self.modelReset.emit()

    def removeRows(self, row, count, parent=QModelIndex()):
        if row < 0 or row + count > len(self._data):
            return False

        self.beginRemoveRows(parent, row, row + count - 1)
        for _ in range(count):
            del self._data[row]

        self.endRemoveRows()
        return True

    def data(self, index: QModelIndex, /, role=...):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return self.posMapping[index.column()][2]

        elif role == Qt.ItemDataRole.ToolTipRole:
            return self.posMapping[index.column()][1]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self.posMapping.keys())

    def headerData(self, section, orientation, /, role=...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.posMapping[section][0]

        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.ToolTipRole:
            return self.posMapping[section][1]

        return super().headerData(section, orientation, role)


class PositionEditorWidget(QGroupBox):
    def __init__(self, parent: QWidget, evtDispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__(title='Positionen', parent=parent)
        self.event_dispatcher = evtDispatcher
        self.evt_store = evtStore
        self.__build_ui()

    def __build_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.position_table = QTableView(self)
        self.position_table.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows)
        self.position_table.setSelectionMode(
            QTableView.SelectionMode.SingleSelection)
        self.position_table_model = PositionTableModel(self)
        self.position_table.setModel(self.position_table_model)
        self.position_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents)
        self.position_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents)
        self.position_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents)
        self.position_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch)
        self.position_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.position_table)

        self.formWidget = QWidget(self)
        layout.addWidget(self.formWidget)
        self.formWidget.setLayout(QGridLayout())

        self.txtLfdNr = QLineEdit('', self.formWidget)
        self.txtLfdNr.textEdited.connect(self.check_positiondata_complete)
        self.txtLfdNr.setFixedWidth(50)
        self.txtLfdNr.setValidator(QIntValidator())
        self.txtSellerAssignedId = QLineEdit('', self.formWidget)
        self.txtSellerAssignedId.setMinimumWidth(100)
        self.txtSellerAssignedId.textEdited.connect(
            self.check_positiondata_complete)
        self.txtGlobalId = QLineEdit('', self.formWidget)
        self.txtGlobalId.setMinimumWidth(100)
        self.txtGlobalId.textEdited.connect(self.check_positiondata_complete)
        self.txtName = QLineEdit('', self.formWidget)
        self.txtName.setMinimumWidth(200)
        self.txtName.textEdited.connect(self.check_positiondata_complete)
        self.txtPrice = QLineEdit(
            '', self.formWidget, alignment=Qt.AlignmentFlag.AlignRight)
        self.txtPrice.setValidator(QDoubleValidator(0.0, 9999.99, 3))
        self.txtPrice.textEdited.connect(self.check_positiondata_complete)

        self.lblLfdNr = QLabel(
            'LfdNr', self, alignment=Qt.AlignmentFlag.AlignRight)
        self.lblSellerAssignedId = QLabel(
            'Artikel-Nr', self, alignment=Qt.AlignmentFlag.AlignRight)
        self.lblGlobalId = QLabel(
            'GTIN', self, alignment=Qt.AlignmentFlag.AlignRight)
        self.lblName = QLabel('Bezeichnung', self,
                              alignment=Qt.AlignmentFlag.AlignRight)
        self.lblPrice = QLabel('Einzelpreis', self,
                               alignment=Qt.AlignmentFlag.AlignRight)

        self.formWidget.layout().addWidget(self.lblLfdNr, 0, 0)
        self.formWidget.layout().addWidget(self.txtLfdNr, 0, 1)
        self.formWidget.layout().addWidget(self.lblSellerAssignedId, 0, 3)
        self.formWidget.layout().addWidget(self.txtSellerAssignedId, 0, 4)
        self.formWidget.layout().addWidget(self.lblGlobalId, 0, 5)
        self.formWidget.layout().addWidget(self.txtGlobalId, 0, 6)

        self.formWidget.layout().addWidget(self.lblName, 1, 0)
        self.formWidget.layout().addWidget(self.txtName, 1, 1, 1, 4)
        self.formWidget.layout().addWidget(self.lblPrice, 1, 5)
        self.formWidget.layout().addWidget(self.txtPrice, 1, 6)

        self.btn_grp = QFrame(self)
        self.btn_ok = QPushButton('Position hinzufügen')
        self.btn_ok.setEnabled(False)
        self.btn_ok.clicked.connect(self.add_position)
        self.btn_grp.setLayout(QHBoxLayout())
        self.btn_grp.layout().addStretch(1)
        self.btn_grp.layout().addWidget(self.btn_ok)
        layout.addWidget(self.btn_grp)

        # Kontextmenü per Rechtsklick aktivieren
        self.position_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.position_table.customContextMenuRequested.connect(
            self.open_context_menu)

    def check_positiondata_complete(self, text) -> None:
        """Prüft, ob alle zwingenden Positionsdaten für eine neue Position vorhanden sind"""
        if len(self.txtLfdNr.text()) > 0 and \
                len(self.txtSellerAssignedId.text()) > 0 and \
                len(self.txtName.text()) > 0 and \
                len(self.txtPrice.text()):
            self.btn_ok.setEnabled(True)
        else:
            self.btn_ok.setEnabled(False)

    def add_position(self):
        """Fügt eine Position in die Liste ein"""
        locale = QLocale()
        self.position_table_model.addPosition(
            idx=int(self.txtLfdNr.text()),
            art_nr=self.txtSellerAssignedId.text(),
            gtin=self.txtGlobalId.text(),
            name=self.txtName.text(),
            price=float(locale.toDouble(self.txtPrice.text())[0])
        )
        self.clear_inputs()
        self.txtLfdNr.setFocus()

    def clear_inputs(self):
        """Leert die Eingabefelder"""
        self.txtLfdNr.setText('')
        self.txtSellerAssignedId.setText('')
        self.txtGlobalId.setText('')
        self.txtName.setText('')
        self.txtPrice.setText('')

    def open_context_menu(self, pos: QPoint):
        # Index unter dem Mauszeiger ermitteln
        index = self.position_table.indexAt(pos)
        if not index.isValid():
            return  # außerhalb von Zeilen geklickt

        row = index.row()

        menu = QMenu(self)
        act_delete = QAction("Zeile löschen", self)
        menu.addAction(act_delete)

        # Action verbinden
        act_delete.triggered.connect(lambda: self.delete_row(row))

        # Menü an globaler Mausposition öffnen
        global_pos = self.position_table.viewport().mapToGlobal(pos)
        menu.exec(global_pos)

    def delete_row(self, row: int):
        # Optional: Sicherheitsabfrage, Mehrfachauswahl, etc.
        self.position_table_model.removeRows(row, 1)


class HeaderWidget(QFrame):
    """Der Kopf mit den generellen Daten zur Erfassung"""

    def __init__(self, parent: QWidget, evtDispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__(parent=parent)
        self.evtStore = evtStore
        self.event_dispatcher = evtDispatcher
        self.supplierReader = SupplierReader(self.evtStore)
        self.__build_ui()
        self.__register_events()

    def __register_events(self):
        self.cmbSupplier.currentIndexChanged.connect(
            lambda e: self.check_header_infos_changed())

        self.cmb_doctype.currentIndexChanged.connect(
            lambda e: self.check_header_infos_changed())

        self.txtFldDocId.textChanged.connect(
            lambda e: self.check_header_infos_changed())

        self.txtFldDocDate.dateChanged.connect(
            lambda e: self.check_header_infos_changed())

    def __build_ui(self):
        __headLayout = QGridLayout(self)
        self.setLayout(__headLayout)
        self.lblSelectSupplier = QLabel('Lieferant zuordnen', self)
        self.cmbSupplier = QComboBox(self, editable=False)
        self.cmbSupplier.addItem('<keiner>', None)

        __headLayout.addWidget(self.lblSelectSupplier, 0, 0)
        __headLayout.addWidget(self.cmbSupplier, 0, 1, 1, 2)

        self.lblDocType = QLabel('Dokumenttyp', self)
        self.lblDocId = QLabel('Dokument-ID', self)
        self.lblDocDate = QLabel('Dokumentdatum', self)

        __headLayout.addWidget(self.lblDocType, 1, 0)
        __headLayout.addWidget(self.lblDocId, 1, 1, 1, 2)
        __headLayout.addWidget(self.lblDocDate, 1, 3)
        __headLayout.setColumnStretch(7, 1)

        self.cmb_doctype = QComboBox(self, editable=False)
        self.cmb_doctype.addItem('<bitte wählen>', None)
        self.cmb_doctype.addItem('Rechnung', 'invoice')
        self.cmb_doctype.addItem('Bestellung', 'order')

        self.txtFldDocId = QLineEdit(
            parent=self, placeholderText='Dok-Id, z.B. ReNr')
        self.txtFldDocId.setMinimumWidth(200)

        self.txtFldDocDate = QDateEdit(parent=self)
        self.txtFldDocDate.setCalendarPopup(True)
        self.txtFldDocDate.setDisplayFormat("dd.MM.yyyy")
        self.txtFldDocDate.setDate(QDate.currentDate())
        self.txtFldDocDate.setMaximumDate(QDate.currentDate())

        self.btnSavePositions = QPushButton('Erfassung speichern', self)
        self.btnSavePositions.setEnabled(False)

        __headLayout.addWidget(self.cmb_doctype, 2, 0)
        __headLayout.addWidget(self.txtFldDocId, 2, 1, 1, 2)
        __headLayout.addWidget(self.txtFldDocDate, 2, 3)
        __headLayout.addWidget(self.btnSavePositions, 2, 4)
        __headLayout.setColumnStretch(5, 1)

    def check_header_infos_changed(self):
        """Prüft, ob bei Veränderungen der Header-Eingabefelder die MUSS-Werte gesetzt wurden"""
        doc_id = self.txtFldDocId.text()
        doc_date = self.txtFldDocDate.text()
        suppl_id = self.cmbSupplier.currentData()
        doc_type = self.cmb_doctype.currentData()

        if len(doc_id) > 0 and \
                len(doc_date) > 0 and \
                suppl_id is not None and \
                doc_type is not None:
            self.btnSavePositions.setEnabled(True)
        else:
            self.btnSavePositions.setEnabled(False)

    def showEvent(self, event):
        suppliers: List[Supplier] = self.supplierReader.read_all()
        self.cmbSupplier.clear()
        self.cmbSupplier.addItem('')
        for s in suppliers:
            self.cmbSupplier.addItem(s.suppl_name, userData=s.suppl_id)
        return super().showEvent(event)


class ManualPositionEditorWidget(QGroupBox):
    """Dient der manuellen Erfassung von Positionen"""

    def __init__(self, parent: QWidget, evt_dispatcher: EventDispatcher, evt_store: EventStore):
        super().__init__('Manuelle Positionserfassung', parent=parent)
        self.evt_dispatcher = evt_dispatcher
        self.evt_store = evt_store
        self.__build_ui()

    def __build_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.header_widget = HeaderWidget(
            self, self.evt_dispatcher, self.evt_store)
        layout.addWidget(self.header_widget)

        self.positions_widget = PositionEditorWidget(
            self, self.evt_dispatcher, self.evt_store)
        layout.addWidget(self.positions_widget)

        layout.addStretch(1)
        layout.addWidget(StatusMessageWidget(self, self.evt_dispatcher))
