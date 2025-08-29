
from pydantic import BaseModel
from datetime import datetime
from datetime import timezone
import uuid

REGISTERED_EVENTS = {
    'supplier.onboarded': "Es wurde ein neuer Lieferant hinzugefügt"
}

class Event(BaseModel):
    id: uuid.UUID | None = None
    position: int | None = None
    version: int | None = None
    specversion: str = '1.0'
    datacontenttype: str = 'application/json'
    source: str = 'dorfladen-schlichten.de/dlrech/events'
    type: str
    subject: str
    time: datetime
    data: str | None = None

    @classmethod
    def createEvent(cls, id: uuid.uuid1, subject: str, type: str, data: str):
        if type not in REGISTERED_EVENTS.keys():
            raise LookupError(f"event type 'type' is unknown")

        evt = cls(id=id, type=type, subject=subject,
                  time=datetime.now(timezone.utc), data=data)
        return evt
