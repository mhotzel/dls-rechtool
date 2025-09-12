
from datetime import date
from typing import List

from pydantic import BaseModel

from domain.event_factory import GenericInvoice, GenericOrder
from domain.order_confirmation import OrderConfirmation
from domain.xinvoice import Invoice
from services.event_store.event import Event, EvtTypes
from services.event_store.eventstore import EventStore


class Document(BaseModel):
    doc_date: date
    doc_type: str
    doc_id: str
    suppl_id: str
    suppl_name: str
    doc_state: str | None = None


class FindInvoiceAndOrderEventsCmd:
    """Command zum Finden der Rechnungen und Bestellungen gemäß der Suchparameter"""

    def __init__(self, date_from: date, date_to: date, suppl_id: str, issue_id: str, evt_store: EventStore):
        self.date_from = date_from
        self.date_to = date_to
        self.suppl_id = suppl_id if suppl_id else ''
        self.issue_id = issue_id if issue_id else ''
        self.evt_store = evt_store

    def findAll(self) -> List[Document]:
        """Liefert die gefundenen Events als Liste zurück"""

        invoices = self.evt_store.readEventsByType(
            EvtTypes.INVOICE_IMPORTED.value)
        order_confs = self.evt_store.readEventsByType(
            EvtTypes.ORDERCONF_IMPORTED.value)
        generic_invoices = self.evt_store.readEventsByType(
            EvtTypes.GENERIC_INVOICE_IMPORTED.value)
        
        generic_orders = self.evt_store.readEventsByType(
            EvtTypes.GENERIC_ORDER_IMPORTED.value)

        result: List[Document] = []

        for item in invoices:
            if (self.issue_id == 'invoice' or self.issue_id == ''):
                inv = Invoice.model_validate_json(item.data)
                if self.date_from <= inv.invoice_date and self.date_to >= inv.invoice_date and (inv.invoice_seller_id == self.suppl_id or self.suppl_id == ''):
                    result.append(Document(doc_date=inv.invoice_date, doc_type='invoice', doc_id=inv.invoice_id,
                                  suppl_id=inv.invoice_seller_id, suppl_name=inv.invoice_seller_name))

        for item in order_confs:
            if (self.issue_id == 'order_confirmation' or self.issue_id == ''):
                order = OrderConfirmation.model_validate_json(item.data)
                if self.date_from <= order.order_date and self.date_to >= order.order_date and (order.suppl_id == self.suppl_id or self.suppl_id == ''):
                    result.append(Document(doc_date=order.order_date, doc_type='order_confirmation',
                                  doc_id=order.order_confirm_id, suppl_id=order.suppl_id, suppl_name=order.suppl_name))

        for item in generic_invoices:
            if (self.issue_id == 'invoice' or self.issue_id == ''):
                doc = GenericInvoice.model_validate_json(item.data)
                if self.date_from <= doc.invoice_date and self.date_to >= doc.invoice_date and (self.suppl_id == doc.suppl_id or self.suppl_id == ''):
                    result.append(Document(doc_date=doc.invoice_date, doc_type='invoice',
                                            doc_id=doc.invoice_id, suppl_id=doc.suppl_id, suppl_name=doc.suppl_name))
                
        for item in generic_orders:
            if (self.issue_id == 'order' or self.issue_id == ''):
                doc = GenericOrder.model_validate_json(item.data)
                if self.date_from <= doc.order_date and self.date_to >= doc.order_date and (self.suppl_id == doc.suppl_id or self.suppl_id == ''):
                    result.append(Document(doc_date=doc.order_date, doc_type='order',
                                            doc_id=doc.order_id, suppl_id=doc.suppl_id, suppl_name=doc.suppl_name))

        return result
