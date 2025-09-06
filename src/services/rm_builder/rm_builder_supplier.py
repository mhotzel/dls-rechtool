
from typing import Mapping
from services.rm_builder.rm_builder_base import ReadModelBaseBuilder, ReadModelEventHandler
from services.sqlite_conn_manager import SqliteConnectionManager

class ReadModelSupplierBuilder(ReadModelBaseBuilder):
    """
    Implementiert einen Projektor auf einem EventStore,
    der beim Start alle noch nicht verarbeiteten Events
    die Lieferanten betreffend anhand der letzten
    verarbeiteten Position erkennt und verarbeitet.
    """

    def __init__(
        self, conn_mgr: SqliteConnectionManager,
        handlers: Mapping[str, ReadModelEventHandler],
        target_table: str
    ):
        super().__init__(conn_mgr, handlers, target_table)

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
