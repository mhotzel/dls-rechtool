

from typing import List
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QFrame, QComboBox
from PySide6.QtCore import QSize

from application.event_dispatcher import EventDispatcher
from domain.supplier_reader import SupplierReader
from domain.suppliers import Supplier
from services.event_store.eventstore import EventStore


class ImportEInvoice(QWidget):
    """Oberflaeche zur Steuerung des Imports von E-Rechnungen"""

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher, evtStore: EventStore):
        super().__init__(parent=parent)
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
        self.chkAlreadyImported = QCheckBox('Rechnung wurde bereits importiert', self.headFrame)
        self.chkAlreadyImported.setEnabled(False)
        
        __headLayout.addWidget(self.txtFldSupplier, 2, 0)
        __headLayout.addWidget(self.txtFldInvoiceNr, 2, 1)
        __headLayout.addWidget(self.txtFldInvoiceDate, 2, 2)
        __headLayout.addWidget(self.chkAlreadyImported, 2, 3)
        __headLayout.addWidget(self.btnLoadInVoice, 2, 4)

        self.bodyFrame.setMinimumHeight(400)
        self.bodyFrame.setMinimumSize(QSize(500, 400))

    def showEvent(self, event):
        suppliers: List[Supplier] = self.supplierReader.read_all()
        self.cmbSupplier.clear()
        self.cmbSupplier.addItem('')
        for s in suppliers:
            self.cmbSupplier.addItem(s.suppl_name, userData=s.suppl_id)
        return super().showEvent(event)