from typing import List, MutableMapping, Sequence
import dataclasses
from PySide6.QtWidgets import QTableView, QGroupBox, QWidget, QHBoxLayout, QHeaderView, QAbstractItemView
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from application.app_event import AppEvent
from application.event_dispatcher import EventDispatcher
from domain.fakturx_invoice import FakturXInvoicePosition
import locale


class InvoicePosTableModel(QAbstractTableModel):

    def __init__(self, parent: QWidget, data: Sequence[FakturXInvoicePosition]):
        super().__init__(parent)
        self._data: Sequence[FakturXInvoicePosition] = data
        locale.setlocale(locale.LC_ALL, '')

        self.posMapping = {
            0: ('LfdNr', 'Laufende Nummer'),
            1: ('Pos-Nr', 'Positionsnummer aus der Rechnung'),
            2: ('GTIN', 'i.d.R. die EAN'),
            3: ('ArtNr', 'Artikelnummer des Lieferanten'),
            4: ('Bezeichnung', 'Artikelbezeichnung des Lieferanten'),
            5: ('Einz.Preis. B', 'Listen-Einzelpreis ohne Zu- oder Abschläge'),
            6: ('Menge B', 'Menge zum Listen-Einzelpreis'),
            7: ('ME B', 'Mengeneinheit zum Listen-Einzelpreis'),
            8: ('Einz.Preis N', 'Einzelpreis nach Zu- und Abschlägen'),
            9: ('Menge N', 'Menge zum Einzelpreis nach Zu- und Abschlägen'),
            10: ('ME N', 'Mengeneinheit nach Zu- und Abschlägen'),
            11: ('Menge ber.', 'Menge zur Berechnung des Gesamtpreises'),
            12: ('ME', 'Mengeneinheit der Menge zur Berechnung des Gesamtpreises'),
            13: ('USt %', 'Umsatzsteuersatz'),
            14: ('Gesamtpreis', 'Gesamtpreis')
        }

    def data(self, index: QModelIndex, /, role=...):
        pos = self._data[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            match index.column():
                case 0: return self.getDefaultValue(pos.idx)
                case 1: return self.getDefaultValue(pos.lineId)
                case 2: return self.getDefaultValue(pos.globalproductId[0]) + ' (' + self.getDefaultValue(pos.globalproductId[1]) + ')'
                case 3: return self.getDefaultValue(pos.sellerAssignedId)
                case 4: return self.getDefaultValue(pos.name)
                case 5: return self.getValueAsCurrency(pos.grossPriceProductTradePrice.chargeAmount)
                case 6: return self.getFloatValue(pos.grossPriceProductTradePrice.basisQuantity)
                case 7: return self.getDefaultValue(pos.grossPriceProductTradePrice.unitCode)
                case 8: return self.getValueAsCurrency(pos.netPriceProductTradePrice.chargeAmount)
                case 9: return self.getFloatValue(pos.netPriceProductTradePrice.basisQuantity)
                case 10: return self.getDefaultValue(pos.netPriceProductTradePrice.unitCode)
                case 11: return self.getFloatValue(pos.billedQuantity)
                case 12: return self.getDefaultValue(pos.billedQuantityUnitCode)
                case 13: return self.getFloatValue(pos.applicableTradeTax.rateApplicablePercent)
                case 14: return self.getValueAsCurrency(pos.lineTotalAmount)
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            match index.column():
                case 0 | 1 | 7 | 10 | 12: return Qt.AlignmentFlag.AlignCenter
                case 2 | 3 | 4: return Qt.AlignmentFlag.AlignLeft
                case 5 | 6 | 8 | 9 | 11 | 13 | 14: return Qt.AlignmentFlag.AlignRight

        elif role == Qt.ItemDataRole.ToolTipRole:
            match index.column():
                case 0: return 'Laufende Nummer'

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return 15

    def headerData(self, section, orientation, /, role=...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.posMapping[section][0]

        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.ToolTipRole:
            return self.posMapping[section][1]

        return super().headerData(section, orientation, role)

    def getValueAsCurrency(self, value: any) -> str:
        """Hilfsfunktion zur Ausgabe eines Wertes als Währungsbetrag"""
        if value:
            return locale.format_string(f="%.3f", val=value, grouping=True, monetary=True)
        return ""

    def getFloatValue(self, value: any, default=''):
        "Hilfsfunktion zur Formatierung von Float-Werten"
        if value:
            return locale.format_string(f="%.3f", val=value, grouping=True)
        return ""

    def getDefaultValue(self, value: any, default=''):
        "Hilfsfunktion zur Formatierung von Float-Werten"
        if value:
            return f"{value}"
        return default


class InvoicePositionsWidget(QGroupBox):
    """Listet die Rechnungspositionen"""

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher):
        super().__init__(title='Eingelesene Rechnungspositionen', parent=parent)
        self.evt_dispatcher = event_dispatcher
        self.invoice_model_filled = False
        self.__build_ui()

    def addInvoiceData(self, invoicePositions: Sequence[FakturXInvoicePosition]) -> None:
        """laedt die Rechnungspositionen"""
        model = InvoicePosTableModel(self, invoicePositions)
        self.tableWidget.setModel(model)
        header = self.tableWidget.horizontalHeader()
        for i in range(15):
            header.setSectionResizeMode(
                i, QHeaderView.ResizeMode.ResizeToContents)
            
        self.invoice_model_filled = True

    def __build_ui(self) -> None:
        """Baut die Oberfläche"""
        layout = QHBoxLayout(self)
        self.setLayout(layout)
        self.tableWidget = QTableView(parent=self)
        self.tableWidget.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows)
        layout.addWidget(self.tableWidget)
