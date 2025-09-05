
from typing import List
from services.event_store.event import Event
from services.event_store.eventstore import EventStore
from services.sqlite_conn_manager import SqliteConnectionManager

SQL = [
    """
    CREATE TABLE IF NOT EXISTS projection_checkpoints (
    name TEXT PRIMARY KEY,
    last_position INTEGER NOT NULL
    );
    ""","""
    CREATE TABLE IF NOT EXISTS rm_suppliers_t (
    supplier_id    TEXT PRIMARY KEY,
    supplier_name  TEXT NOT NULL,
    updated_utc  TEXT NOT NULL
    );
    ""","""
    CREATE INDEX IF NOT EXISTS idx_rm_suppliers ON rm_suppliers_t(supplier_id);
    """
]

class SupplierTableProjector:
    """Basisklasse zur Erzeugung von Read-Models / Projektionen"""

    def __init__(self, conn_manager: SqliteConnectionManager):
        self.conn_manager = conn_manager
        self.name = 'suppliers'

    def setup_tables(self) -> None:
        """Erzeugt die notwendigen Projektions-Tabellen"""
        conn = self.conn_manager.get_connection()
        for stmt in SQL:
            conn.execute(stmt)

    def on_supplier_onboarded(self, evt: List[Event]) -> None:
        """Reagiert auf das Onboarding eines Lieferanten"""

    def __get_last_position(self) -> int:
        conn = self.conn_manager.get_connection()
        cur = conn.execute("SELECT last_position FROM projection_checkpoints WHERE name=?", (self.name,))
        row = cur.fetchone()
        return int(row[0]) if row else 0
    
    def __set_last_position(self, pos: int):
        conn = self.conn_manager.get_connection()
        conn.execute("""
            INSERT INTO projection_checkpoints(name, last_position)
            VALUES(?, ?)
            ON CONFLICT(name) DO UPDATE SET last_position=excluded.last_position
        """, (self.name, pos))

    