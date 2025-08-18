
from datetime import datetime
from datetime import timezone
from typing import Protocol


class BaseEvent:
    """Basisklasse gemäß CloudEvents-Standard"""

    def __init__(self, id: str, subject: str, type: str, data: dict):
        self.id = id
        self.specversion = '1.0'
        self.type = type
        self.source = "dls-rechtool"
        self.subject = subject
        self.datacontenttype = "application/json"
        self.time = datetime.now(timezone.utc)
        self.data = data

    def to_dict(self):
        return {
            'id': self.id,
            'specversion': self.specversion,
            'type': self.type,
            'source': self.source,
            'subject': self.subject,
            'datacontenttype': self.datacontenttype,
            'time': self.time.isoformat(),
            'data': self.data
        }


class EventStore(Protocol):
    """Dient der Speicherung von Events"""

    def save_event(evt: BaseEvent):
        """Stores an Event"""
