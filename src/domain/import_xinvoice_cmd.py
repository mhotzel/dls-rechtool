
from typing import List, Sequence
import uuid

from domain.already_imported_exception import AlreadyImportedException
from domain.event_factory import build_stream_id, invoice_imported_event
from domain.fakturx_invoice import FakturXInvoice
from domain.xinvoice import InvoiceItem, Invoice
from services.event_store.event import Event
from services.readmodels.base_data_store import DataStore, Document


class ImportXInvoiceCmd:
    """Importiert die Daten einer X-Rechnung"""

    def __init__(self, data_store: DataStore, invoice: FakturXInvoice, supplier_id: str):
        self.subject = build_stream_id(
            'invoices', supplier_id, invoice.invoiceNumber)
        self.supplier_id = supplier_id
        self.invoice = invoice
        self.data_store = data_store

    def save_doc(self) -> Event:

        if self._find_doc(self.subject):
            raise AlreadyImportedException(
                f"Das Dokument mit dem Subject '{self.subject}' wurde bereits eingelesen")

        invoice_result = Invoice(
            invoice_id=self.invoice.invoiceNumber,
            invoice_date=self.invoice.invoiceDate,
            invoice_seller_id=self.supplier_id,
            invoice_seller_globalid=self.invoice.sellerGlobalId[0],
            invoice_seller_name=self.invoice.sellerName,
            positions=[]
        )

        inv_item: InvoiceItem = None
        for pos in self.invoice.invoicePositions:
            inv_item = InvoiceItem(
                invoice_id=self.invoice.invoiceNumber,
                invoice_date=self.invoice.invoiceDate,
                invoice_seller_id=self.supplier_id,
                invoice_seller_name=self.invoice.sellerName,
                invoice_seller_globalid=self.invoice.sellerGlobalId[0],
                pos_idx=pos.idx,
                pos_nr=pos.lineId,
                pos_global_id=pos.globalproductId[0],
                pos_seller_id=pos.sellerAssignedId,
                pos_name=pos.name,
                pos_gross_price=pos.grossPriceProductTradePrice.chargeAmount,
                pos_gross_quantity=pos.grossPriceProductTradePrice.basisQuantity,
                pos_gross_unitcode=pos.grossPriceProductTradePrice.unitCode,
                pos_net_price=pos.netPriceProductTradePrice.chargeAmount,
                pos_net_quantity=pos.netPriceProductTradePrice.basisQuantity,
                pos_net_unitcode=pos.netPriceProductTradePrice.unitCode,
                pos_billed_quantity=pos.billedQuantity,
                pos_billed_unitcode=pos.billedQuantityUnitCode,
                pos_tax_percent=pos.applicableTradeTax.rateApplicablePercent,
                pos_total_line_amount=pos.lineTotalAmount
            )
            invoice_result.positions.append(inv_item)

        evt = invoice_imported_event(self.supplier_id, invoice_result)
        return evt

    def _find_doc(self, subject) -> bool:
        """Prüft, ob ein Dokument mit dem angegebenen Subject schon vorhanden ist"""
        docs: List[Document] = self.data_store.get_doc_list()
        for doc in docs:
            if doc.subject == subject:
                return True
        return False
