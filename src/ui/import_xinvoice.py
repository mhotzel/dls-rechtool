

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QFrame, QComboBox
from PySide6.QtCore import Qt, QSize


class ImportEInvoice(QWidget):
    """Oberflaeche zur Steuerung des Imports von E-Rechnungen"""

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)
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