from typing import MutableMapping, List, Callable
from abc import abstractmethod
from application.app_event import AppEvent


class EventDispatcher:

    @abstractmethod
    def send(self, event: AppEvent) -> None:
        """Verarbeitet ein Event"""

    @abstractmethod
    def register(self, topic: str, listener: Callable[[AppEvent], None]) -> None:
        """Registriert einen Listener zum angegebenen Topic. Existiert das Topic nicht, wird ein Fehler ausgelöst"""


class NoSuchEventException(KeyError):

    def __init__(self, *args):
        super().__init__(*args)


class EventDispatcherImpl:
    """Verteilt Events an registrierte Listener"""

    def __init__(self):
        self.__listeners: MutableMapping[str, List[Callable[[AppEvent], None]]] = {}

    def register(self, topic: str, listener: Callable[[AppEvent], None]) -> None:
        """Registriert einen Listener zum angegebenen Topic. Existiert das Topic nicht, wird ein Fehler ausgelöst"""
        if not topic in self.__listeners:
            self.__listeners[topic] = []
        self.__listeners[topic].append(listener)

    def send(self, event: AppEvent) -> None:
        """Verarbeitet ein Event"""

        listeners = self.__listeners.get(event.evt_type)
        if listeners is None:
            return

        l: Callable[[AppEvent], None]
        for l in listeners:
            l(event)
