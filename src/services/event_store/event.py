
from pydantic import BaseModel
from datetime import datetime
from datetime import timezone
import uuid

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
    def createEvent(cls, id: uuid.uuid1, subject: str, type: str):
        evt = cls(id=id, type=type, subject=subject, time=datetime.now(timezone.utc))
        return evt
