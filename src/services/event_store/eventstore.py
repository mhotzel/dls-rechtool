
from abc import abstractmethod
from typing import Protocol, Sequence
import uuid

from services.event_store.event import Event


class EventStore(Protocol):
    """Dient der Speicherung von Events"""

    # keine Versionsprüfung (append regardless)
    EXPECTED_VERSION_NOCHECK = None
    EXPECTED_VERSION_NEW = -1  # Subject MUSS neu sein (keine Events vorhanden)

    @abstractmethod
    def add_event(self, evt: Event, expected_version: int | None) -> None:
        """Fuegt ein Event dem Store hinzu.
        event: Das zu speichernde Event
        expected_version:
           - None  => keine Versionsprüfung (append regardless)
           - int   => aktuelle Subject-Version MUSS == expected_version sein
                      (zur Abbildung optimistischer Concurrency; so wird verhindert, 
                      dass ein anderer Prozess zwischenzeitlich unbemerkt bereits
                      ein Event der gleichen Nummer geschrieben hat)
           - -1    => Subject MUSS neu sein (keine Events vorhanden)
        """

    @abstractmethod
    def readEventsByType(self, evtType: str, from_position: int = 1, limit: int | None = None) -> Sequence[Event]:
        """Ermittelt alle Events zum angegebenen Event Typ.
        from_position => Ab welcher Position soll gelesen werden?
        limit         => Anzahl zu lesender Events
        """

    @abstractmethod
    def readEventById(self, id: uuid.UUID) -> Event:
        """Liefert das Event mit einer bestimmten ID"""

    @abstractmethod
    def readSubject(self, subject: str, from_version: int = 1, limit: int | None = None):
        """Liest alle Events mit dem uebergebenen Subject, also einen 'Stream'.
        from_version  => Ab welcher Version soll gelesen werden?
        limit         => Anzahl zu lesender Events
        """