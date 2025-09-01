
"""Command zur Speicherung manueller Erfassungen"""

from datetime import date, datetime
from typing import List
import uuid

from pydantic import BaseModel

from services.event_store.event import Event


class ManualDocumentPosition(BaseModel):
    """Eine Position"""
    idx: int
    line_id: str
    sellerAssignedId: str
    globalId: str | None = None
    name: str
    price: float


class ManualDocument(BaseModel):
    """Ein Objekt, welches die manuelle Erfassung von Artikelpreisen ermöglicht"""
    seller_id: str
    doc_type: str
    doc_id: str
    doc_date: date
    positions: List[ManualDocumentPosition] = []


def manualPositionsImportedEvent(doc: ManualDocument):
    """Erzeugt ein Event für ein Objekt mir manuell erfassten Positionen"""
    subject: str = f"docid-{doc.doc_id}"
    evt = Event.createEvent(
        uuid.uuid1(),
        subject=subject,
        type='manual-doc.imported',
        data=doc.model_dump_json()
    )
    return evt
