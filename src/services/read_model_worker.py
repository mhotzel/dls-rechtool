
from datetime import datetime, timezone
import json
import sqlite3
from typing import Mapping
from application.app_event import LogLevel
from services.thread_worker import ThreadWorker, Message, Status
from services.event_store.sqlite_eventstore import SqliteEventStore
from services.sqlite_conn_manager import SqliteConnectionManager

SQL = [
    """
CREATE TABLE IF NOT EXISTS rm_suppliers_t (
    suppl_id TEXT PRIMARY KEY,
    suppl_name TEXT,
    updated_ts TEXT NOT NULL
);
""", """
CREATE TABLE IF NOT EXISTS checkpoints_t (
    name TEXT PRIMARY KEY,
    last_position INTEGER NOT NULL
);
"""
]


class ReadModelWorker(ThreadWorker):
    """
    Implementiert einen Projektor auf einem EventStore,
    der beim Start alle noch nicht verarbeiteten Events
    anhand der letzten verarbeiteten Position erkennt und verarbeitet.
    Danach lauscht er auf Nachrichten aus der Anwendung.
    Beim Eintreffen eines Events wird wieder auf Update-Bedarf geprüft. 
    """

    def __init__(self, conn_mgr: SqliteConnectionManager):
        super().__init__(name="ReadModelWorker")
        self.conn_mgr = conn_mgr

        self.handlers = {
            'supplier.onboarded': self.on_supplier_onboarded
        }

    def on_start(self) -> bool:
        self._initial_setup()
        return super().on_start()

    def _initial_setup(self) -> None:
        """
        Prüft auf Vorhandensein des ReadModels in der DB und legt bei Bedarf die
        die Tabellen an.
        """
        conn = self.conn_mgr.get_connection()
        for stmt in SQL:
            conn.execute(stmt)

        self.conn_mgr.close_connection()

    def _get_last_position(self) -> int:
        """Liefert die letzte Position, die lt. Tabelle 'checkpoints_t' verarbeitet wurde"""

        last_pos = 0

        sql = """
        SELECT last_position FROM checkpoints_t WHERE name=?
        """

        conn = self.conn_mgr.get_connection()
        row = conn.execute(sql, ('rm_suppliers_t', )).fetchone()
        if row:
            last_pos = row['last_position']

        self.conn_mgr.close_connection()
        return last_pos

    def _set_last_position(self, new_pos: int, cur: sqlite3.Cursor):
        """Setzt als checkpoint die neue Position"""
        sql = """
        INSERT INTO checkpoints_t (name, last_position)
        VALUES(?, ?)
        ON CONFLICT(name) DO UPDATE SET last_position=excluded.last_position
        """

        cur.execute(sql, ('rm_suppliers_t', new_pos))


    def _run_once(self) -> int:
        """
        Arbeitet alle ausstehenden Events ab. 
        Gibt die zuletzt verarbeitete Position zurück
        """

        last_pos = self._get_last_position()

        sql = """
        SELECT evt.position, evt.type, evt.data
        FROM events_t AS evt
        WHERE evt.position > ?
        AND evt.type IN ('supplier.onboarded')
        ORDER BY evt.position ASC
        """

        conn = self.conn_mgr.get_connection()
        rows = conn.execute(sql, (last_pos, )).fetchall()
        if len(rows) == 0:
            return last_pos

        cur = conn.cursor()
        cur.execute("BEGIN IMMEDIATE;")
        try:
            new_last_pos = last_pos
            for row in rows:
                data = json.loads(row['data'])
                new_last_pos = row['position']
                evt_type = row['type']
                handler = self.handlers[evt_type]
                handler(data, cur)

            self._set_last_position(new_last_pos, cur)
            conn.commit()
            return new_last_pos
        except Exception:
            conn.rollback()
            raise
        finally:
            self.conn_mgr.close_connection()

    def on_supplier_onboarded(self, data: Mapping, cur: sqlite3.Cursor) -> None:
        """Verarbeitet das Onboarden eines Lieferanten"""
        sql = """
        INSERT INTO rm_suppliers_t 
        (suppl_id, suppl_name, updated_ts) 
        VALUES
        (?, ?, ?)
        ON CONFLICT (suppl_id) DO NOTHING
        """

        suppl_id = data['suppl_id']
        suppl_name = data['suppl_name']
        seller_id = data.get('seller_id')
        ts = datetime.now(tz=timezone.utc).isoformat()

        cur.execute(sql, (suppl_id, suppl_name, ts))
