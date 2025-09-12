
from datetime import date
from typing import List

from pydantic import BaseModel

from domain.event_factory import GenericInvoice, GenericOrder
from domain.order_confirmation import OrderConfirmation
from domain.xinvoice import Invoice
from services.event_store.event import Event, EvtTypes
from services.event_store.eventstore import EventStore
from services.readmodels.base_data_store import DataStore


class Document(BaseModel):
    subject: str
    doc_date: date
    doc_type: str
    doc_id: str
    suppl_id: str
    suppl_name: str
    doc_state: str | None = None


class FindInvoiceAndOrderEventsCmd:
    """Command zum Finden der Rechnungen und Bestellungen gemäß der Suchparameter"""

    def __init__(self, date_from: date, date_to: date, suppl_id: str, doc_type: str, evt_store: EventStore, data_store: DataStore):
        self.date_from = date_from
        self.date_to = date_to
        self.suppl_id = suppl_id if suppl_id else ''
        self.doc_type = doc_type if doc_type else ''
        self.evt_store = evt_store
        self.data_store = data_store

    def findAll(self) -> List[Document]:
        """Liefert die gefundenen Events als Liste zurück"""

        docs = self.data_store.get_doc_list()
        doc: Document = docs[0]
        docs = [doc for doc in docs if doc.doc_date >= self.date_from and doc.doc_date <= self.date_to]
        docs = [doc for doc in docs if self.suppl_id == '' or doc.suppl_id == self.suppl_id]
        docs = [doc for doc in docs if self.doc_type == '' or doc.doc_type == self.doc_type]

        return docs
