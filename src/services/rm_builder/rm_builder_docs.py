
from datetime import datetime, timezone
from queue import SimpleQueue
from sqlite3 import Cursor
from typing import List, Mapping
from services.event_store.event import EvtTypes
from services.rm_builder.rm_builder_base import ReadModelBaseBuilder
from services.sqlite_conn_manager import SqliteConnectionManager

INITIAL_TABLE_SETUP = [
    """
CREATE TABLE IF NOT EXISTS rm_documents_t (
    suppl_id TEXT NOT NULL,
    suppl_name TEXT,
    doc_id TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    doc_date TEXT NOT NULL,
    doc_state TEXT,
    updated_ts TEXT NOT NULL
)
""", """
CREATE UNIQUE INDEX IF NOT EXISTS idx_rm_documents ON rm_documents_t(
    suppl_id, doc_id, doc_type
)
""", """
CREATE TABLE IF NOT EXISTS checkpoints_t (
    name TEXT PRIMARY KEY,
    last_position INTEGER NOT NULL
)        
"""
]


def on_invoice_imported(data: Mapping, cur: Cursor) -> List[Exception]:

    sql = """
    INSERT INTO rm_documents_t
    (suppl_id, suppl_name, doc_id, doc_type, doc_date, doc_state, updated_ts)
    VALUES
    (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING
    """

    now = datetime.now(tz=timezone.utc)

    errors: List[Exception] = []

    try:
        cur.execute(sql, (
            data['invoice_seller_id'],
            data['invoice_seller_name'],
            data['invoice_id'],
            'invoice',
            data['invoice_date'],
            None,
            now.isoformat(),
        ))
    except Exception as e:
        errors.append(e)

    return errors

def on_orderconfirmation_imported(data: Mapping, cur: Cursor) -> List[Exception]:
    sql = """
    INSERT INTO rm_documents_t
    (suppl_id, suppl_name, doc_id, doc_type, doc_date, doc_state, updated_ts)
    VALUES
    (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING
    """

    now = datetime.now(tz=timezone.utc)

    errors: List[Exception] = []

    try:
        cur.execute(sql, (
            data['suppl_id'],
            data['suppl_name'],
            data['order_confirm_id'],
            'order_confirmation',
            data['order_date'],
            None,
            now.isoformat(),
        ))
    except Exception as e:
        errors.append(e)

    return errors


def on_generic_invoice_imported(data: Mapping, cur: Cursor) -> List[Exception]:
    sql = """
    INSERT INTO rm_documents_t
    (suppl_id, suppl_name, doc_id, doc_type, doc_date, doc_state, updated_ts)
    VALUES
    (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING
    """

    now = datetime.now(tz=timezone.utc)

    errors: List[Exception] = []

    try:
        cur.execute(sql, (
            data['suppl_id'],
            data['suppl_name'],
            data['invoice_id'],
            'invoice',
            data['invoice_date'],
            None,
            now.isoformat(),
        ))
    except Exception as e:
        errors.append(e)

    return errors


def on_generic_order_imported(data: Mapping, cur: Cursor) -> List[Exception]:
    sql = """
    INSERT INTO rm_documents_t
    (suppl_id, suppl_name, doc_id, doc_type, doc_date, doc_state, updated_ts)
    VALUES
    (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING
    """

    now = datetime.now(tz=timezone.utc)

    errors: List[Exception] = []

    try:
        cur.execute(sql, (
            data['suppl_id'],
            data['suppl_name'],
            data['order_id'],
            'order',
            data['order_date'],
            None,
            now.isoformat(),
        ))
    except Exception as e:
        errors.append(e)

    return errors


class RmDocumentListBuilder(ReadModelBaseBuilder):
    """Schreibt das ReadModel der Rechnungs- und Bestellungstabelle"""

    def __init__(self, conn_mgr: SqliteConnectionManager, status_queue: SimpleQueue):

        self.status_queue = status_queue

        self.handlers = {
            EvtTypes.INVOICE_IMPORTED.value: on_invoice_imported,
            EvtTypes.ORDERCONF_IMPORTED.value: on_orderconfirmation_imported,
            EvtTypes.GENERIC_INVOICE_IMPORTED.value: on_generic_invoice_imported,
            EvtTypes.GENERIC_ORDER_IMPORTED.value: on_generic_order_imported
        }
        super().__init__(conn_mgr, self.handlers, 'rm_documents_t', self.status_queue)

    def _initial_setup(self):
        conn = self.conn_mgr.get_connection()
        with conn:
            for stmt in INITIAL_TABLE_SETUP:
                conn.execute(stmt)
