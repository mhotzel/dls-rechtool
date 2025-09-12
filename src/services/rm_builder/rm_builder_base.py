
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
from queue import SimpleQueue
from sqlite3 import Cursor
from typing import Callable, List, Mapping
from application.app_event import AppEvent, LogLevel
from services.sqlite_conn_manager import SqliteConnectionManager

ReadModelEventHandler = Callable[[Cursor, Mapping], List[Exception]]


def set_last_position(new_pos: int, rm_table: str, cur: Cursor):
    """Setzt als checkpoint die neue Position"""
    sql = """
    INSERT INTO checkpoints_t (name, last_position)
    VALUES(?, ?)
    ON CONFLICT(name) DO UPDATE SET last_position=excluded.last_position
    """

    cur.execute(sql, (rm_table, new_pos))


def get_last_position(rm_table: str, cur: Cursor) -> int:
    """Liefert die letzte Position, die lt. Tabelle 'checkpoints_t' verarbeitet wurde"""

    last_pos = 0

    sql = """
    SELECT last_position FROM checkpoints_t WHERE name=?
    """

    row = cur.execute(sql, (rm_table, )).fetchone()
    if row:
        last_pos = row['last_position']

    return last_pos


class ReadModelBaseBuilder(ABC):
    """
    Implementiert einen Projektor auf einem EventStore,
    der beim Start alle noch nicht verarbeiteten Events
    des übergebenen Typs anhand der letzten
    verarbeiteten Position erkennt und verarbeitet.
    Diese Klasse dient als Basisklasse.
    Insbesondere die Methode '_initial_setup' ist zu
    überschreiben, um die notwendigen Tabellen initial 
    aufzubauen. 
    """

    def __init__(
        self, conn_mgr: SqliteConnectionManager,
        handlers: Mapping[str, ReadModelEventHandler],
        target_table: str,
        status_queue: SimpleQueue
    ):
        self.conn_mgr = conn_mgr
        self._handlers = handlers
        self._target_table = target_table
        self.status_queue = status_queue
        self._initial_setup()

    @abstractmethod
    def _initial_setup(self) -> None:
        """
        Prüft auf Vorhandensein des ReadModels in der DB und legt bei Bedarf die
        die Tabellen an.
        """

    def run(self) -> int:
        """
        Arbeitet alle ausstehenden Events ab. 
        Gibt die zuletzt verarbeitete Position zurück
        """

        events = [f"'{key}'" for key in self._handlers.keys()]
        events_str = ', '.join(events)

        sql = f"""
        SELECT evt.position, evt.type, evt.data
        FROM events_t AS evt
        WHERE evt.position > ?
        AND evt.type IN ({events_str})
        ORDER BY evt.position ASC
        """

        conn = self.conn_mgr.get_connection()

        cur = conn.cursor()
        cur.execute("BEGIN IMMEDIATE;")
        try:
            last_pos = get_last_position(self._target_table, cur)
            rows = cur.execute(sql, (last_pos, )).fetchall()
            if len(rows) == 0:

                return last_pos

            new_last_pos = last_pos
            for row in rows:
                data = json.loads(row['data'])
                new_last_pos = row['position']
                evt_type = row['type']
                handler = self._handlers[evt_type]
                errors = handler(data, cur)
                if errors:
                    for e in errors:
                        self.status_queue.put(AppEvent(evt_lvl=LogLevel.CRITICAL, evt_type='status-message', evt_data=e))

            set_last_position(new_last_pos, self._target_table, cur)
            conn.commit()
            return new_last_pos
        except Exception:
            conn.rollback()
            raise
        finally:
            self.conn_mgr.close_connection()
