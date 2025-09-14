"""Unterstützt die Erzeugung fachlicher Events"""

from datetime import date
import json
from urllib.parse import quote
from typing import List
import uuid

from pydantic import BaseModel, Field
from domain.order_confirmation import OrderConfirmation
from domain.xinvoice import Invoice
from services.event_store.event import Event, EvtTypes


class GenericDocPosition(BaseModel):
    """Eine Position"""
    idx: int
    line_id: str
    sellerAssignedId: str
    globalId: str | None = None
    name: str
    price: float

class GenericDocument(BaseModel):
    """Ein generisches Dokument, welches die manuelle Erfassung von Artikelpreisen ermöglicht"""
    doctype: str
    suppl_id: str
    suppl_name: str
    doc_id: str
    doc_date: date
    positions: List[GenericDocPosition] | None = []

class GenericInvoicePosition(GenericDocPosition):
    """Eine Position einer Rechnung"""
    idx: int
    line_id: str
    sellerAssignedId: str
    globalId: str | None = None
    name: str
    price: float


class GenericInvoice(BaseModel):
    """Eine generische Rechnung, welche die manuelle Erfassung von Artikelpreisen ermöglicht"""
    suppl_id: str
    suppl_name: str
    invoice_id: str
    invoice_date: date
    positions: List[GenericInvoicePosition] = []


class GenericOrderPosition(GenericDocPosition):
    """Eine Position einer Bestellung"""


class GenericOrder(BaseModel):
    """Eine generische Bestellung, welche die manuelle Erfassung von Artikelpreisen ermöglicht"""
    suppl_id: str
    suppl_name: str
    order_id: str
    order_date: date
    positions: List[GenericOrderPosition] = []


class Supplier(BaseModel):
    """Ein Lieferant"""
    suppl_id: str
    suppl_name: str
    seller_id: str | None = None

    def __str__(self):
        if self.seller_id:
            return f"{self.suppl_name}    ({self.suppl_id} / {self.seller_id})"
        else:
            return f"{self.suppl_name}    ({self.suppl_id})"


def build_stream_id(aggregate: str, *components: str) -> str:
    """baut ein URL-angelehntes Subject und glättet alles in Kleinschreibung sowie codiert die Pfadkomponenten URL-sicher"""
    sep = '/'
    components = [quote(c.lower(), safe='') for c in components]
    result = sep.join([aggregate.lower(), *components])
    return result


def supplier_onboarded_event(supplier: Supplier) -> Event:
    """Erzeugt ein 'supplier.onboarded' Event """

    subject = build_stream_id('suppliers', supplier.suppl_id)
    data = supplier.model_dump_json()
    return Event.createEvent(
        id=uuid.uuid1(),
        subject=subject,
        type=EvtTypes.SUPPLIER_ONBOARDED,
        data=data
    )


def invoice_imported_event(supplier_id, invoice: Invoice) -> Event:
    """Erzeugt ein 'invoice.imported' Event"""

    subject = build_stream_id(
        'invoices', invoice.invoice_seller_id, invoice.invoice_id)
    evt = Event.createEvent(
        id=uuid.uuid1(),
        subject=subject,
        type=EvtTypes.INVOICE_IMPORTED,
        data=invoice.model_dump_json()
    )
    return evt


def orderconfirmation_imported_event(order_conf: OrderConfirmation) -> Event:

    subject = build_stream_id('orderconfirmations',
                              order_conf.suppl_id, order_conf.order_confirm_id)
    evt = Event.createEvent(
        uuid.uuid1(),
        subject=subject,
        type=EvtTypes.ORDERCONF_IMPORTED,
        data=order_conf.model_dump_json()
    )
    return evt


def generic_invoice_imported_event(doc: GenericInvoice) -> Event:
    """Erzeugt ein Event für ein Objekt mit manuell erfassten Positionen"""
    subject = build_stream_id('generic_invoices', doc.suppl_id, doc.invoice_id)
    evt = Event.createEvent(
        uuid.uuid1(),
        subject=subject,
        type=EvtTypes.GENERIC_INVOICE_IMPORTED,
        data=doc.model_dump_json()
    )
    return evt


def generic_order_imported_event(doc: GenericOrder) -> Event:
    """Erzeugt ein Event für ein Objekt mit manuell erfassten Positionen"""
    subject = build_stream_id('generic_orders', doc.suppl_id, doc.order_id)
    evt = Event.createEvent(
        uuid.uuid1(),
        subject=subject,
        type=EvtTypes.GENERIC_ORDER_IMPORTED,
        data=doc.model_dump_json()
    )
    return evt


def document_voided_event(subject: str) -> Event:

    subject = build_stream_id(subject)
    evt = Event.createEvent(
        uuid.uuid1(),
        subject=subject,
        type=EvtTypes.DOCUMENT_VOIDED,
        data=json.dumps(dict(), ensure_ascii=False)
    )
    return evt


def document_unvoided_event(subject: str) -> Event:

    subject = build_stream_id(subject)
    evt = Event.createEvent(
        uuid.uuid1(),
        subject=subject,
        type=EvtTypes.DOCUMENT_UNVOIDED,
        data=json.dumps(dict(), ensure_ascii=False)
    )
    return evt
