from typing import List
import uuid
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFormLayout, QListWidgetItem,
    QHBoxLayout, QGroupBox, QListWidget, QFrame, QLineEdit, QMessageBox
)

from PySide6.QtCore import Qt

from application.app_event import AppEvent
from application.event_dispatcher import EventDispatcher
from domain.onboard_supplier_cmd import OnboardSupplierCommand, SupplierAlreadyExistsException
from domain.supplier_reader import SupplierReader
from domain.suppliers import Supplier
from services.event_store.eventstore import EventStore
from services.event_store.event import Event
from ui.status_msg_widget import StatusMessageWidget


class SupplierListWidget(QGroupBox):
    """Listet die Lieferanten auf"""

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__(title='Lieferanten pflegen', parent=parent)
        self.evtStore: EventStore = evtStore
        self.evt_dispatcher = event_dispatcher
        self.__build_ui()

        self.evt_dispatcher.register(
            'suppliers-changed', lambda e: self.suppliers_changed())

        self.suppliers_changed()

    def __build_ui(self):
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        self.suppliersListWidget = QListWidget(self)
        layout.addWidget(self.suppliersListWidget)

        self.buttonGroup = QFrame(self)
        layout.addWidget(self.buttonGroup)

        btn_grp_layout = QVBoxLayout(self.buttonGroup)
        self.buttonGroup.setLayout(btn_grp_layout)
        self.btn_edit = QPushButton('Ändern')
        self.btn_edit.setEnabled(False)
        self.btn_delete = QPushButton('Löschen')
        self.btn_delete.setEnabled(False)
        btn_grp_layout.addWidget(self.btn_edit)
        btn_grp_layout.addWidget(self.btn_delete)
        btn_grp_layout.addStretch(1)

    def suppliers_changed(self):
        """Updated die Lieferanten"""
        sr = SupplierReader(self.evtStore)
        suppliers: List[Supplier] = sr.read_all()
        self.suppliersListWidget.clear()
        for sup in suppliers:
            self.suppliersListWidget.addItem(str(sup))


class SupplierEditWidget(QGroupBox):
    """Pane zur Bearbeitung eines Lieferanten"""

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__(title='Lieferant bearbeiten', parent=parent)
        self.evtStore: EventStore = evtStore
        self.evt_dispatcher = event_dispatcher
        self.__build_ui()

    def __build_ui(self):
        vlayout = QVBoxLayout(self)
        self.formWidget = QWidget(self)
        form = QFormLayout(parent=self.formWidget,
                           labelAlignment=Qt.AlignmentFlag.AlignRight)
        self.txt_suppl_id = QLineEdit(parent=self)
        self.txt_suppl_name = QLineEdit(parent=self)
        self.txt_seller_id = QLineEdit(parent=self)
        form.addRow('DLS-eigene Lieferanten-ID', self.txt_suppl_id)
        form.addRow('Name', self.txt_suppl_name)
        form.addRow('externe ID des Lieferanten', self.txt_seller_id)
        vlayout.addWidget(self.formWidget)

        self.btn_grp = QFrame(self)
        self.btn_cancel = QPushButton('abbrechen')
        self.btn_cancel.clicked.connect(self.clear_inputs)
        self.btn_ok = QPushButton('Speichern')
        self.btn_ok.clicked.connect(self.save_supplier)
        self.btn_grp.setLayout(QHBoxLayout())
        self.btn_grp.layout().addStretch(1)
        self.btn_grp.layout().addWidget(self.btn_cancel)
        self.btn_grp.layout().addWidget(self.btn_ok)

        vlayout.addWidget(self.btn_grp)

    def clear_inputs(self) -> None:
        """Bricht die Bearbeitung ab"""
        self.txt_suppl_id.setText('')
        self.txt_suppl_name.setText('')
        self.txt_seller_id.setText('')

    def save_supplier(self) -> None:
        """Speichert die Lieferantendaten"""

        s_reader = SupplierReader(self.evtStore)
        try:
            supplier = OnboardSupplierCommand(
                suppliers=s_reader.read_all(),
                suppl_id=self.txt_suppl_id.text(),
                suppl_name=self.txt_suppl_name.text(),
                seller_id=self.txt_seller_id.text()
            )()

            evt = Event.createEvent(
                id=uuid.uuid1(),
                subject=f"supplier-{supplier.suppl_id}",
                type='supplier.onboarded',
                data=supplier.model_dump_json()
            )

            self.evtStore.add_event(evt, expected_version=-1)
            self.evt_dispatcher.send(AppEvent(
                evt_type='status-message', evt_data=f"INFO: Lieferant '{supplier.suppl_name}' wurde erfolgreich angelegt"))
            self.evt_dispatcher.send(AppEvent(evt_type='suppliers-changed'))
            self.clear_inputs()

        except SupplierAlreadyExistsException as se:
            msg = f"CRITICAL: Es ist bereits ein Lieferant mit der ID '{self.txt_suppl_id.text()}' vorhanden"
            QMessageBox.critical(
                self, 'Fehler bei der Anlage des Lieferanten', msg)
            self.evt_dispatcher.send(
                AppEvent(evt_type='status-message', evt_data=msg))

        except ValueError as ve:
            msg = f"CRITICAL: Lieferanten ohne ID sind nicht zulässig"
            QMessageBox.critical(
                self, 'Fehler bei der Anlage des Lieferanten', msg)
            self.evt_dispatcher.send(
                AppEvent(evt_type='status-message', evt_data=msg))


class SuppliersEditorWidget(QWidget):
    """Pane, welche die Anzeige und die Bearbeitungsmöglichkeit von Lieferanten kombiniert darstellt"""

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__(parent)
        self.evtStore: EventStore = evtStore
        self.evt_dispatcher = event_dispatcher
        self.__build_ui()

    def __build_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        layout.addWidget(SupplierListWidget(
            self, self.evt_dispatcher, self.evtStore))
        layout.addWidget(SupplierEditWidget(
            self, self.evt_dispatcher, self.evtStore))
        layout.addWidget(StatusMessageWidget(self, self.evt_dispatcher))
        layout.addStretch(1)
