

from typing import List
from PySide6.QtWidgets import (
    QWidget, QGroupBox, QGridLayout, QLabel, QFileDialog,
    QLineEdit, QPushButton, QVBoxLayout, QFrame, QComboBox
)
from PySide6.QtCore import QSize

from application.app_event import AppEvent, LogLevel
from application.event_dispatcher import EventDispatcher
from domain.import_xinvoice_cmd import ImportXInvoiceCmd
from domain.supplier_reader import SupplierReader
from domain.event_factory import Supplier
from domain.zugferd_invoice import ZugferdInvoiceDocument
from services.event_store.eventstore import EventStore
from ui.invoice_positions_widget import InvoicePositionsWidget


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
        self.event_dispatcher.register('invoice-positions-loaded', lambda e: self.check_import_ready())

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
        self.cmbSupplier.currentIndexChanged.connect(
            lambda evt: self.check_import_ready())

        __headLayout.addWidget(self.lblSelectSupplier, 0, 0)
        __headLayout.addWidget(self.cmbSupplier, 0, 1, 1, 2)

        self.lblSupplier = QLabel('Lieferant', self.headFrame)
        self.lblInvoiceNr = QLabel('Rechnungsnummer', self.headFrame)
        self.lblInvoiceDate = QLabel('Rechnungsdatum', self.headFrame)

        __headLayout.addWidget(self.lblSupplier, 1, 0)
        __headLayout.addWidget(self.lblInvoiceNr, 1, 3)
        __headLayout.addWidget(self.lblInvoiceDate, 1, 4)
        __headLayout.setColumnStretch(7, 1)

        self.txtFldSupplier = QLineEdit(parent=self.headFrame, readOnly=True)
        self.txtFldInvoiceNr = QLineEdit(parent=self.headFrame, readOnly=True)
        self.txtFldInvoiceDate = QLineEdit(
            parent=self.headFrame, readOnly=True)
        self.btnLoadInVoice = QPushButton('Rechnung laden', self.headFrame)
        self.btnLoadInVoice.clicked.connect(self.load_invoice)
        self.btnSaveInVoice = QPushButton('Rechnung speichern', self.headFrame)
        self.btnSaveInVoice.setEnabled(False)
        self.btnSaveInVoice.clicked.connect(self.save_invoice)

        __headLayout.addWidget(self.txtFldSupplier, 2, 0, 1, 3)
        __headLayout.addWidget(self.txtFldInvoiceNr, 2, 3)
        __headLayout.addWidget(self.txtFldInvoiceDate, 2, 4)
        __headLayout.addWidget(self.btnLoadInVoice, 2, 5)
        __headLayout.addWidget(self.btnSaveInVoice, 2, 6)

        self.invoiceWidget.setMinimumHeight(400)
        self.invoiceWidget.setMinimumSize(QSize(500, 400))

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
            self.event_dispatcher.send(
                AppEvent(
                    evt_lvl=LogLevel.WARN,
                    evt_type='status-message',
                    evt_data='Es wurde keine PDF-Datei ausgewählt'
                )
            )
            return

        self.invoice_doc = ZugferdInvoiceDocument(pdf_file=pdf_file)
        self.invoiceWidget.addInvoiceData(
            invoicePositions=self.invoice_doc.invoice.invoicePositions)
        self.txtFldInvoiceDate.setText(
            self.invoice_doc.invoice.invoiceDate.strftime('%d.%m.%Y'))
        self.txtFldInvoiceNr.setText(self.invoice_doc.invoice.invoiceNumber)
        self.txtFldSupplier.setText(self.invoice_doc.invoice.sellerName)
        self.event_dispatcher.send(
            AppEvent(
                evt_lvl=LogLevel.INFO,
                evt_type='status-message',
                evt_data='Rechnung wurde erfolgreich zu Anzeige geladen'
            )
        )

    def check_import_ready(self) -> None:
        """Prueft, ob die Rechnung gespeichert werden kann"""
        if self.cmbSupplier.currentData() and self.invoiceWidget.tableWidget.model():
            self.btnSaveInVoice.setEnabled(True)
        else:
            self.btnSaveInVoice.setEnabled(False)

    def clear_inputs(self):
        """Setzt die Eingabefelder zurück"""
        self.cmbSupplier.setCurrentIndex(0)
        self.txtFldInvoiceDate.setText('')
        self.txtFldInvoiceNr.setText('')
        self.txtFldSupplier.setText('')
        self.invoice_doc = None
        self.invoiceWidget.tableWidget.setModel(None)

    def save_invoice(self):
        """Speichert die Rechnungspositionen in der Datenbank"""
        supplier_id: str = str(self.cmbSupplier.currentData())
        subject = f"invoice-{supplier_id}-{self.txtFldInvoiceNr.text()}"

        try:
            events = self.evtStore.readEventsBySubject(subject=subject, limit=1)
            event_to_save = ImportXInvoiceCmd(
                events=events, invoice=self.invoice_doc.invoice, supplier_id=supplier_id)()

            self.evtStore.add_event(evt=event_to_save, expected_version=-1)
            self.event_dispatcher.send(
                AppEvent(
                    evt_lvl=LogLevel.INFO,
                    evt_type='status-message',
                    evt_data='Rechnungsdaten wurden gespeichert')
            )
            self.clear_inputs()
        except Exception as e:
            self.event_dispatcher.send(
                AppEvent(
                    evt_lvl=LogLevel.CRITICAL,
                    evt_type='status-message',
                    evt_data=f"Rechnungsdaten '{subject}' wurden nicht gespeichert: {e}"
                )
            )
