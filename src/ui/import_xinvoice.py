

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QFrame, QHBoxLayout, QSpacerItem
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
        self.lblSupplier = QLabel('Lieferant', self.headFrame)
        self.lblInvoiceNr = QLabel('Rechnungsnummer', self.headFrame)
        self.lblInvoiceDate = QLabel('Rechnungsdatum', self.headFrame)
        __headLayout.addWidget(self.lblSupplier, 0, 0)
        __headLayout.layout().addWidget(self.lblInvoiceNr, 0, 1)
        __headLayout.layout().addWidget(self.lblInvoiceDate, 0, 2)
        __headLayout.setColumnStretch(4, 1)

        self.txtFldSupplier = QLineEdit(parent=self.headFrame, readOnly=True)
        self.txtFldInvoiceNr = QLineEdit(parent=self.headFrame, readOnly=True)
        self.txtFldInvoiceDate = QLineEdit(
            parent=self.headFrame, readOnly=True)
        self.btnLoadInVoice = QPushButton('Rechnung laden', self.headFrame)
        __headLayout.layout().addWidget(self.txtFldSupplier, 1, 0)
        __headLayout.layout().addWidget(self.txtFldInvoiceNr, 1, 1)
        __headLayout.layout().addWidget(self.txtFldInvoiceDate, 1, 2)
        __headLayout.layout().addWidget(self.btnLoadInVoice, 1, 3)

        self.bodyFrame.setMinimumHeight(400)
        self.bodyFrame.setMinimumSize(QSize(500, 400))