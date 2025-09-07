
from datetime import datetime, timezone
from sqlite3 import Cursor
from typing import Mapping
from services.rm_builder.rm_builder_base import ReadModelBaseBuilder
from services.sqlite_conn_manager import SqliteConnectionManager


def on_invoice_imported(data: Mapping, cur: Cursor) -> None:
    """
    Verarbeitet den Import einer Rechnung.
    Event: 'invoice.imported'
    """
    sql = """
    INSERT INTO rm_product_list_t 
    (suppl_id, suppl_name, issue_type, issue_id, issue_date, seller_assigned_id, global_id, name, price, updated_ts) 
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING
    """

    suppl_id = data['invoice_seller_id']
    suppl_name = data['invoice_seller_name']
    issue_type = 'invoice'
    issue_id = data['invoice_id']
    issue_date = data['invoice_date']
    positions = data['positions']
    updated_ts = datetime.now(tz=timezone.utc).isoformat()

    for pos in positions:
        seller_assigned_id = pos['pos_seller_id']
        global_id = pos.get('pos_global_id')
        price = pos['pos_gross_price']
        name = pos['pos_name']

        cur.execute(sql, (suppl_id, suppl_name, issue_type, issue_id,
                        issue_date, seller_assigned_id, global_id, name, price, updated_ts))


def on_orderconfirmation_imported(data: Mapping, cur: Cursor) -> None:
    """
    Verarbeitet den Import einer Bestellbestätigung
    Event: 'orderconf.imported', Subject: 'orderconfirmation-1-xxx'
    """
    sql = """
    INSERT INTO rm_product_list_t 
    (suppl_id, suppl_name, issue_type, issue_id, issue_date, seller_assigned_id, global_id, name, price, updated_ts) 
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING
    """

    suppl_id = data['suppl_id']
    suppl_name = data['suppl_name']
    issue_type = 'order_confirmation'
    issue_id = data['order_confirm']
    issue_date = data['order_date']
    positions = data['positions']
    updated_ts = datetime.now(tz=timezone.utc).isoformat()

    for pos in positions:
        seller_assigned_id = pos['seller_assigned_id']
        global_id = pos.get('global_id')
        price = pos['price']
        name = pos['name']

        cur.execute(sql, (suppl_id, suppl_name, issue_type, issue_id,
                        issue_date, seller_assigned_id, global_id, name, price, updated_ts))


def on_manualdoc_imported(data: Mapping, cur: Cursor) -> None:
    """
    Verarbeitet den Import eines manuellen Dokuments
    Event: 'manual-doc.imported', Subject: 'docid-2-<docid>'
    """
    sql = """
    INSERT INTO rm_product_list_t 
    (suppl_id, suppl_name, issue_type, issue_id, issue_date, seller_assigned_id, global_id, name, price, updated_ts) 
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING
    """

    suppl_id = data['suppl_id']
    suppl_name = data['suppl_name']
    issue_type = data['doc_type']
    issue_id = data['doc_id']
    issue_date = data['doc_date']
    positions = data['positions']
    updated_ts = datetime.now(tz=timezone.utc).isoformat()

    for pos in positions:
        seller_assigned_id = pos['sellerAssignedId']
        global_id = pos.get('globalId')
        price = pos['price']
        name = pos['name']

        cur.execute(sql, (suppl_id, suppl_name, issue_type, issue_id,
                        issue_date, seller_assigned_id, global_id, name, price, updated_ts))


class RmProductListBuilder(ReadModelBaseBuilder):
    """
    Implementiert einen Projektor auf einem EventStore,
    der beim Start alle noch nicht verarbeiteten Events
    Rechnungs- und Bestelleingänge betreffend anhand der letzten
    verarbeiteten Position erkennt und verarbeitet.
    """

    def __init__(self, conn_mgr: SqliteConnectionManager):
        super().__init__(
            conn_mgr=conn_mgr,
            handlers={
                'invoice.imported': on_invoice_imported,
                'orderconf.imported': on_orderconfirmation_imported,
                'manual-doc.imported': on_manualdoc_imported
            },
            target_table='rm_product_list_t'
        )

    def _initial_setup(self) -> None:
        """
        Prüft auf Vorhandensein des ReadModels in der DB und legt bei Bedarf die
        die Tabellen an.
        """

        SQL = [
            """
        CREATE TABLE IF NOT EXISTS rm_product_list_t (
            suppl_id TEXT NOT NULL,
            suppl_name TEXT NOT NULL,
            issue_type TEXT NOT NULL,
            issue_id TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            seller_assigned_id TEXT NOT NULL,
            global_id TEXT,
            name TEXT NOT NULL,
            price float NOT NULL,
            updated_ts TEXT NOT NULL
        )
        """, """
        CREATE TABLE IF NOT EXISTS checkpoints_t (
            name TEXT PRIMARY KEY,
            last_position INTEGER NOT NULL
        )        
        ""","""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_rm_product_list ON rm_product_list_t(
            issue_id, seller_assigned_id, issue_type
        )
        """
        ]

        conn = self.conn_mgr.get_connection()
        for stmt in SQL:
            conn.execute(stmt)

        self.conn_mgr.close_connection()
