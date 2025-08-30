

from typing import List
from PySide6.QtWidgets import (
    QWidget, QGroupBox, QGridLayout, QLabel, QFileDialog,
    QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QFrame, QComboBox
)
from PySide6.QtCore import QSize

from application.app_event import AppEvent
from application.event_dispatcher import EventDispatcher
from domain.supplier_reader import SupplierReader
from domain.suppliers import Supplier
from domain.zugferd_invoice import ZugferdInvoiceDocument
from services.event_store.eventstore import EventStore
from ui.status_msg_widget import StatusMessageWidget


class ImportEInvoice(QGroupBox):
    """Oberflaeche zur Steuerung des Imports von E-Rechnungen"""

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__(parent=parent, title='Rechnungsbearbeitung')
        self.evtStore: EventStore = evtStore
        self.event_dispatcher: EventDispatcher = event_dispatcher
        self.supplierReader = SupplierReader(self.evtStore)
        self.__build_ui()

    def __build_ui(self):
        """Baut die Oberfläche"""
        self.setLayout(QVBoxLayout(self))

        self.headFrame = QFrame(self)
        self.bodyFrame = QFrame(self)
        self.layout().addWidget(self.headFrame)
        self.layout().addWidget(self.bodyFrame, stretch=1)

        __headLayout = QGridLayout(self.headFrame)
        self.headFrame.setLayout(__headLayout)

        self.lblSelectSupplier = QLabel('Lieferant auswählen', self)
        self.cmbSupplier = QComboBox(self, editable=False)
        self.cmbSupplier.addItem('<keiner>', None)
        self.cmbSupplier.addItem('EDEKA', 1)
        self.cmbSupplier.addItem('Kurz', 2)

        __headLayout.addWidget(self.lblSelectSupplier, 0, 0)
        __headLayout.addWidget(self.cmbSupplier, 0, 1, 1, 2)

        self.lblSupplier = QLabel('Lieferant', self.headFrame)
        self.lblInvoiceNr = QLabel('Rechnungsnummer', self.headFrame)
        self.lblInvoiceDate = QLabel('Rechnungsdatum', self.headFrame)

        __headLayout.addWidget(self.lblSupplier, 1, 0)
        __headLayout.addWidget(self.lblInvoiceNr, 1, 1)
        __headLayout.addWidget(self.lblInvoiceDate, 1, 2)
        __headLayout.setColumnStretch(5, 1)

        self.txtFldSupplier = QLineEdit(parent=self.headFrame, readOnly=True)
        self.txtFldInvoiceNr = QLineEdit(parent=self.headFrame, readOnly=True)
        self.txtFldInvoiceDate = QLineEdit(
            parent=self.headFrame, readOnly=True)
        self.btnLoadInVoice = QPushButton('Rechnung laden', self.headFrame)
        self.btnLoadInVoice.clicked.connect(self.load_invoice)
        self.chkAlreadyImported = QCheckBox(
            'Rechnung wurde bereits importiert', self.headFrame)
        self.chkAlreadyImported.setEnabled(False)

        __headLayout.addWidget(self.txtFldSupplier, 2, 0)
        __headLayout.addWidget(self.txtFldInvoiceNr, 2, 1)
        __headLayout.addWidget(self.txtFldInvoiceDate, 2, 2)
        __headLayout.addWidget(self.chkAlreadyImported, 2, 3)
        __headLayout.addWidget(self.btnLoadInVoice, 2, 4)

        self.bodyFrame.setMinimumHeight(400)
        self.bodyFrame.setMinimumSize(QSize(500, 400))
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
            self.event_dispatcher.send(AppEvent(evt_type='status-message', evt_data='WARN: Es wurde keine PDF-Datei ausgewählt'))
            return

        invoice_doc = ZugferdInvoiceDocument(pdf_file=pdf_file)
        print(invoice_doc.invoice)
