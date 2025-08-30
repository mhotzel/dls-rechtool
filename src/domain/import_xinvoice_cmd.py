
from typing import List, Sequence
import uuid

from application.app_event import AppEvent
from domain.already_imported_exception import AlreadyImportedException
from domain.fakturx_invoice import FakturXInvoice
from domain.suppliers import Supplier
from domain.invoice_item import InvoiceItem
from services.event_store.event import Event
from services.event_store.eventstore import EventStore

class ImportXInvoiceCmd:
    """Importiert die Daten einer X-Rechnung"""

    def __init__(self, events: Sequence[Event], invoice: FakturXInvoice, supplier_id: str) -> Supplier:
        self.subject = f"invoice-{supplier_id}-{invoice.invoiceNumber}"
        self.supplier_id = supplier_id
        self.invoice = invoice
        if len(events) > 0:
                raise AlreadyImportedException(
                    f"invoice with invoice-nr '{invoice.invoiceNumber}' (subject '{self.subject}') was already imported")

    def __call__(self) -> List[Event]:
        result: List[Event] = []
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
            evt = Event.createEvent(
                id=uuid.uuid1(),
                subject=self.subject,
                type='invoiceitem.imported',
                data=inv_item.model_dump_json()
            )
            result.append(evt)
        return result

