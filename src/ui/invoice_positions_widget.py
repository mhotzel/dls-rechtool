from typing import List, MutableMapping, Sequence
import dataclasses
from PySide6.QtWidgets import QTableView, QGroupBox, QWidget, QHBoxLayout
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from application.event_dispatcher import EventDispatcher
from domain.fakturx_invoice import FakturXInvoicePosition
import locale

class InvoicePosTableModel(QAbstractTableModel):

    def __init__(self, parent: QWidget, data: Sequence[FakturXInvoicePosition]):
        super().__init__(parent)
        self._data: Sequence[FakturXInvoicePosition] = data
        locale.setlocale(locale.LC_ALL, '')
    
        self.posMapping = {
            0: 'LfdNr',
            1: 'Pos-Nr',
            2: 'GTIN',
            3: 'Liefer.-ArtNr',
            4: 'Bezeichnung',
            5: 'Std-Einzelpreis',
            6: 'Menge',
            7: 'Mengeneinheit',
            8: 'Einzelpreis',
            9: 'Menge',
            10: 'Mengeneinheit',
            11: 'Berechn. Menge',
            12: 'Berechn. Mengeneinheit',
            13: 'Steuersatz',
            14: 'Gesamtpreis'
        }

    def data(self, index: QModelIndex, /, role = ...):
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

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return 15

    def headerData(self, section, orientation, /, role = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.posMapping[section]
        return super().headerData(section, orientation, role)
    
    def getValueAsCurrency(self, value: any) -> str:
        """Hilfsfunktion zur Ausgabe eines Wertes als Währungsbetrag"""
        if value:
            return locale.format_string(f="%.3f", val=value, grouping=True, monetary=True)
        return ""

    def getFloatValue(self, value: any, default = ''):
        "Hilfsfunktion zur Formatierung von Float-Werten"
        if value:
            return locale.format_string(f="%.3f", val=value, grouping=True)
        return ""

    def getDefaultValue(self, value: any, default = ''):
        "Hilfsfunktion zur Formatierung von Float-Werten"
        if value:
            return f"{value}"
        return default

class InvoicePostionsWidget(QGroupBox):
    """Listet die Rechnungspositionen"""

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher):
        super().__init__(title='Eingelesene Rechnungspositionen', parent=parent)
        self.evt_dispatcher = event_dispatcher
        self.__build_ui()

    def addInvoiceData(self, invoicePositions: Sequence[FakturXInvoicePosition]) -> None:
        """laedt die Rechnungspositionen"""
        model = InvoicePosTableModel(self, invoicePositions)
        self.tableWidget.setModel(model)

    def __build_ui(self) -> None:
        """Baut die Oberfläche"""
        layout = QHBoxLayout(self)
        self.setLayout(layout)
        self.tableWidget = QTableView(parent=self)
        layout.addWidget(self.tableWidget)
