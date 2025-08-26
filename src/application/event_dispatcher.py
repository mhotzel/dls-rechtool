from typing import MutableMapping, List
from abc import abstractmethod
from application.app_event import Listener, AppEvent


class EventDispatcher:

    @abstractmethod
    def send(self, event: AppEvent):
        """Verarbeitet ein Event"""


class NoSuchEventException(KeyError):

    def __init__(self, *args):
        super().__init__(*args)


class EventDispatcherImpl:
    """Verteilt Events an registrierte Listener"""

    def __init__(self):
        self.__listeners: MutableMapping[str, List[Listener]] = {}

    def register(self, topic: str, listener: Listener):
        """Registriert einen Listener zum angegebenen Topic. Existiert das Topic nicht, wird ein Fehler ausgelöst"""
        if not topic in self.__listeners:
            self.__listeners[topic] = []
        self.__listeners[topic].append(listener)

    def send(self, event: AppEvent):
        """Verarbeitet ein Event"""

        listeners = self.__listeners.get(event.evt_type)
        if listeners is None:
            raise NoSuchEventException(f"event '{event.evt_type}' is unknown")

        for l in listeners:
            l.process(event)
