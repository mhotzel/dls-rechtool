
from datetime import datetime, timezone
from queue import SimpleQueue
from sqlite3 import Cursor
from typing import List, Mapping
from services.event_store.event import EvtTypes
from services.rm_builder.rm_builder_base import ReadModelBaseBuilder
from services.sqlite_conn_manager import SqliteConnectionManager


def on_invoice_imported(data: Mapping, cur: Cursor) -> List[Exception]:
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

    errors: List[Exception] = []

    for pos in positions:
        seller_assigned_id = pos['pos_seller_id']
        global_id = pos.get('pos_global_id')
        price = pos['pos_gross_price']
        name = pos['pos_name']

        try:
            cur.execute(sql, (suppl_id, suppl_name, issue_type, issue_id,
                              issue_date, seller_assigned_id, global_id, name, price, updated_ts))
        except Exception as e:
            errors.append(e)

    return errors


def on_orderconfirmation_imported(data: Mapping, cur: Cursor) -> List[Exception]:
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
    issue_id = data['order_confirm_id']
    issue_date = data['order_date']
    positions = data['positions']
    updated_ts = datetime.now(tz=timezone.utc).isoformat()

    errors: List[Exception] = []

    for pos in positions:
        seller_assigned_id = pos['seller_assigned_id']
        global_id = pos.get('global_id')
        price = pos['price']
        name = pos['name']

        try:
            cur.execute(sql, (suppl_id, suppl_name, issue_type, issue_id,
                              issue_date, seller_assigned_id, global_id, name, price, updated_ts))
        except Exception as e:
            errors.append(e)

    return errors


def on_generic_invoice_imported(data: Mapping, cur: Cursor) -> List[Exception]:
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
    issue_type = 'invoice'
    invoice_id = data['invoice_id']
    invoice_date = data['invoice_date']
    positions = data['positions']
    updated_ts = datetime.now(tz=timezone.utc).isoformat()

    errors: List[Exception] = []

    for pos in positions:
        seller_assigned_id = pos['sellerAssignedId']
        global_id = pos.get('globalId')
        price = pos['price']
        name = pos['name']

        try:
            cur.execute(sql, (suppl_id, suppl_name, issue_type, invoice_id,
                              invoice_date, seller_assigned_id, global_id, name, price, updated_ts))
        except Exception as e:
            errors.append(e)

    return errors

def on_generic_order_imported(data: Mapping, cur: Cursor) -> List[Exception]:
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
    issue_type = 'order'
    order_id = data['order_id']
    order_date = data['order_date']
    positions = data['positions']
    updated_ts = datetime.now(tz=timezone.utc).isoformat()

    errors: List[Exception] = []
    for pos in positions:
        seller_assigned_id = pos['sellerAssignedId']
        global_id = pos.get('globalId')
        price = pos['price']
        name = pos['name']

        try:
            cur.execute(sql, (suppl_id, suppl_name, issue_type, order_id,
                          order_date, seller_assigned_id, global_id, name, price, updated_ts))
        except Exception as e:
            errors.append(e)

    return errors


class RmProductListBuilder(ReadModelBaseBuilder):
    """
    Implementiert einen Projektor auf einem EventStore,
    der beim Start alle noch nicht verarbeiteten Events
    Rechnungs- und Bestelleingänge betreffend anhand der letzten
    verarbeiteten Position erkennt und verarbeitet.
    """

    def __init__(self, conn_mgr: SqliteConnectionManager, status_queue: SimpleQueue):
        super().__init__(
            conn_mgr=conn_mgr,
            handlers={
                EvtTypes.INVOICE_IMPORTED.value: on_invoice_imported,
                EvtTypes.ORDERCONF_IMPORTED.value: on_orderconfirmation_imported,
                EvtTypes.GENERIC_INVOICE_IMPORTED.value: on_generic_invoice_imported,
                EvtTypes.GENERIC_ORDER_IMPORTED.value: on_generic_order_imported
            },
            target_table='rm_product_list_t',
            status_queue=status_queue
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
        """, """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_rm_product_list ON rm_product_list_t(
            suppl_id, issue_id, seller_assigned_id, issue_type
        )
        """
        ]

        conn = self.conn_mgr.get_connection()
        for stmt in SQL:
            conn.execute(stmt)

        self.conn_mgr.close_connection()
