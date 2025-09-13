
from typing import List
from domain.xinvoice import InvoiceItem
from services.event_store.eventstore import EventStore


class InvoiceItemReader:
    """Liest Lieferanten aus dem Event Store"""

    def __init__(self, evt_store: EventStore):
        self.evt_store = evt_store

    def read_all(self, subject: str) -> List[InvoiceItem]:
        """Liest alle Lieferanten"""

        events = self.evt_store.readEventsBySubject()

        result: List[InvoiceItem] = []
        for e in events:
            s: InvoiceItem = InvoiceItem.model_validate_json(e.data)
            result.append(s)
        return result
