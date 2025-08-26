from abc import abstractmethod, ABC


class AppEvent:
    """Ein Event, welches durch die UI ausgelöst und an einen Listener gesendet wird."""

    evt_type: str
    evt_data: str | None = None

    def __init__(self, evt_type: str, evt_data: str | None = None):
        self.evt_type = evt_type
        self.evt_data = evt_data


class Listener(ABC):
    """Interface für Listener"""
    
    @abstractmethod
    def process(self, event: AppEvent) -> None:
        """Verarbeitet das Event"""
        ...
