

import datetime
from typing import List
import uuid
from PySide6.QtWidgets import (
    QWidget, QGroupBox, QGridLayout, QLabel, QFileDialog,
    QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QFrame, QComboBox
)
from PySide6.QtCore import QSize

from application.app_event import AppEvent
from application.event_dispatcher import EventDispatcher
from domain.import_xinvoice_cmd import ImportXInvoiceCmd
from domain.invoice_item import InvoiceItem
from domain.invoice_pos_reader import InvoiceItemReader
from domain.supplier_reader import SupplierReader
from domain.suppliers import Supplier
from domain.zugferd_invoice import ZugferdInvoiceDocument
from services.event_store.eventstore import EventStore
from ui.status_msg_widget import StatusMessageWidget
from ui.invoice_positions_widget import InvoicePositionsWidget
from services.event_store.event import Event


class InvoiceAlreadyImportedException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ImportEInvoice(QGroupBox):
    """Oberflaeche zur Steuerung des Imports von E-Rechnungen"""

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__(parent=parent, title='Rechnungsbearbeitung')
        self.evtStore: EventStore = evtStore
        self.event_dispatcher: EventDispatcher = event_dispatcher
        self.supplierReader = SupplierReader(self.evtStore)
        self.invoice_doc: ZugferdInvoiceDocument = None
        self.__build_ui()

    def __build_ui(self):
        """Baut die Oberfläche"""
        self.setLayout(QVBoxLayout(self))

        self.headFrame = QFrame(self)
        self.invoiceWidget = InvoicePositionsWidget(
            self, self.event_dispatcher)
        self.layout().addWidget(self.headFrame)
        self.layout().addWidget(self.invoiceWidget)

        __headLayout = QGridLayout(self.headFrame)
        self.headFrame.setLayout(__headLayout)

        self.lblSelectSupplier = QLabel('Lieferant zuordnen', self)
        self.cmbSupplier = QComboBox(self, editable=False)
        self.cmbSupplier.addItem('<keiner>', None)
        self.cmbSupplier.addItem('EDEKA', 1)
        self.cmbSupplier.addItem('Kurz', 2)
        self.cmbSupplier.currentIndexChanged.connect(
            lambda evt: self.supplier_selected())

        __headLayout.addWidget(self.lblSelectSupplier, 0, 0)
        __headLayout.addWidget(self.cmbSupplier, 0, 1, 1, 2)

        self.lblSupplier = QLabel('Lieferant', self.headFrame)
        self.lblInvoiceNr = QLabel('Rechnungsnummer', self.headFrame)
        self.lblInvoiceDate = QLabel('Rechnungsdatum', self.headFrame)

        __headLayout.addWidget(self.lblSupplier, 1, 0)
        __headLayout.addWidget(self.lblInvoiceNr, 1, 2)
        __headLayout.addWidget(self.lblInvoiceDate, 1, 3)
        __headLayout.setColumnStretch(7, 1)

        self.txtFldSupplier = QLineEdit(parent=self.headFrame, readOnly=True)
        self.txtFldInvoiceNr = QLineEdit(parent=self.headFrame, readOnly=True)
        self.txtFldInvoiceDate = QLineEdit(
            parent=self.headFrame, readOnly=True)
        self.btnLoadInVoice = QPushButton('Rechnung laden', self.headFrame)
        self.btnLoadInVoice.clicked.connect(self.load_invoice)
        self.btnSaveInVoice = QPushButton('Rechnung speichern', self.headFrame)
        self.btnSaveInVoice.setEnabled(False)
        self.btnSaveInVoice.clicked.connect(self.save_invoice_positions)

        __headLayout.addWidget(self.txtFldSupplier, 2, 0, 1, 3)
        __headLayout.addWidget(self.txtFldInvoiceNr, 2, 3)
        __headLayout.addWidget(self.txtFldInvoiceDate, 2, 4)
        __headLayout.addWidget(self.btnLoadInVoice, 2, 5)
        __headLayout.addWidget(self.btnSaveInVoice, 2, 6)

        self.invoiceWidget.setMinimumHeight(400)
        self.invoiceWidget.setMinimumSize(QSize(500, 400))
        self.statusWidget = StatusMessageWidget(self, self.event_dispatcher)
        self.layout().addWidget(self.statusWidget)

    def showEvent(self, event):
        suppliers: List[Supplier] = self.supplierReader.read_all()
        self.cmbSupplier.clear()
        self.cmbSupplier.addItem('')
        for s in suppliers:
            self.cmbSupplier.addItem(s.suppl_name, userData=s.suppl_id)
        return super().showEvent(event)

    def load_invoice(self) -> None:
        """Laedt das Rechnungsdokument und extrahiert die X-Rechnung"""

        pdf_file, _ = QFileDialog.getOpenFileName(
            self, 'Rechnungsdokument auswählen',
            filter='PDF-E-Rechnung (*pdf)'
        )

        if not pdf_file:
            self.event_dispatcher.send(AppEvent(
                evt_type='status-message', evt_data='WARN: Es wurde keine PDF-Datei ausgewählt'))
            return

        self.invoice_doc = ZugferdInvoiceDocument(pdf_file=pdf_file)
        self.invoiceWidget.addInvoiceData(
            invoicePositions=self.invoice_doc.invoice.invoicePositions)
        self.txtFldInvoiceDate.setText(
            self.invoice_doc.invoice.invoiceDate.strftime('%d.%m.%Y'))
        self.txtFldInvoiceNr.setText(self.invoice_doc.invoice.invoiceNumber)
        self.txtFldSupplier.setText(self.invoice_doc.invoice.sellerName)
        self.event_dispatcher.send(AppEvent(
            evt_type='status-message', evt_data='INFO: Rechnung wurde erfolgreich zu Anzeige geladen'))

    def supplier_selected(self):
        """Es wurde ein Lieferant gewählt"""
        if self.cmbSupplier.currentData() and self.invoiceWidget.invoice_model_filled:
            self.btnSaveInVoice.setEnabled(True)
        else:
            self.btnSaveInVoice.setEnabled(False)

    def save_invoice_positions(self):
        """Speichert die Rechnungspositionen in der Datenbank"""
        supplier_id: str = str(self.cmbSupplier.currentData())
        subject = f"invoice-{supplier_id}-{self.txtFldInvoiceNr.text()}"

        try:
            events = self.evtStore.readSubject(subject=subject, limit=1)
            events_to_save = ImportXInvoiceCmd(
                events=events, invoice=self.invoice_doc.invoice, supplier_id=supplier_id)()

            for evt in events_to_save:
                self.evtStore.add_event(evt=evt, expected_version=None)
                self.event_dispatcher.send(
                    AppEvent(
                        evt_type='status-message',
                        evt_data='INFO:Rechnungsdaten wurden gespeichert')
                )
        except Exception as e:
            self.event_dispatcher.send(
                AppEvent(
                    evt_type='status-message',
                    evt_data=f"CRITICAL:Rechnungsdaten '{subject}' wurden nicht gespeichert: {e}"
                )
            )
