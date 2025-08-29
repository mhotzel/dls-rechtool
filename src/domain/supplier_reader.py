
from typing import List
from domain.suppliers import Supplier
from services.event_store.eventstore import EventStore


class SupplierReader:
    """Liest Lieferanten aus dem Event Store"""

    def __init__(self, evt_store: EventStore):
        self.evt_store = evt_store

    def read_all(self) -> List[Supplier]:
        """Liest alle Lieferanten"""

        events = self.evt_store.readEventsByType(evtType='supplier.onboarded')

        result: List[Supplier] = []
        for e in events:
            s: Supplier = Supplier.model_validate_json(e.data)
            result.append(s)
        return result
