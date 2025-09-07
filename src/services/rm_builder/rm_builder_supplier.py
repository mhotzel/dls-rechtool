
from datetime import datetime, timezone
from sqlite3 import Cursor
from typing import Mapping
from services.rm_builder.rm_builder_base import ReadModelBaseBuilder, ReadModelEventHandler
from services.sqlite_conn_manager import SqliteConnectionManager


def on_supplier_onboarded(data: Mapping, cur: Cursor) -> None:
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


class RmSupplierBuilder(ReadModelBaseBuilder):
    """
    Implementiert einen Projektor auf einem EventStore,
    der beim Start alle noch nicht verarbeiteten Events
    die Lieferanten betreffend anhand der letzten
    verarbeiteten Position erkennt und verarbeitet.
    """

    def __init__(
        self, conn_mgr: SqliteConnectionManager
    ):
        super().__init__(
            conn_mgr,
            handlers={
                'supplier.onboarded': on_supplier_onboarded
            },
            target_table='rm_suppliers_t'
        )

    def _initial_setup(self) -> None:
        """
        Prüft auf Vorhandensein des ReadModels in der DB und legt bei Bedarf die
        die Tabellen an.
        """

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

        conn = self.conn_mgr.get_connection()
        for stmt in SQL:
            conn.execute(stmt)

        self.conn_mgr.close_connection()
