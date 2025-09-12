
from datetime import date
from pathlib import Path
from queue import SimpleQueue
from typing import List
from domain import event_factory
from domain.find_inv_order_events_cmd import Document
from domain.order_confirmation import OrderConfirmation
from domain.xinvoice import Invoice, InvoiceItem
from services.event_store.event import EvtTypes
from services.event_store.sqlite_eventstore import SqliteEventStore
from services.readmodels.sqlite_data_store import SqliteDataStore
from services.rm_builder.rm_builder_docs import RmDocumentListBuilder
from services.sqlite_conn_manager import SqliteConnectionManager


def setup(db_path: str) -> SqliteConnectionManager:
    db_file = Path('testdb.sqlite')
    ab_path = db_file.absolute()
    db_file.unlink(missing_ok=True)

    conn_mgr = SqliteConnectionManager()
    conn_mgr.dbFile = str(ab_path)
    return conn_mgr


def teardown(db_path: Path, conn_mgr: SqliteConnectionManager):
    conn_mgr.close_connection()
    db_path.unlink(missing_ok=True)


def test_tables_initialized():
    """Testet, ob die Tabellen alle angelegt wurden"""

    db_file = Path('testdb.sqlite')
    status_queue = SimpleQueue()
    conn_mgr = setup(db_file)
    builder = RmDocumentListBuilder(conn_mgr, status_queue=status_queue)

    conn = conn_mgr.get_connection()
    try:
        conn.execute("SELECT * FROM checkpoints_t")
        conn.execute("SELECT * FROM rm_documents_t")
    except Exception as e:
        assert e is None
    finally:
        conn_mgr.close_connection()

    teardown(db_file, conn_mgr)


def test_invoices():
    """Testet, ob normale Rechnungen verarbeitet werden"""

    db_file = Path('testdb.sqlite')
    conn_mgr = setup(db_file)
    status_queue = SimpleQueue()
    builder = RmDocumentListBuilder(conn_mgr, status_queue)
    evt_store = SqliteEventStore(conn_mgr)

    evt_invoice_imported = event_factory.invoice_imported_event(
        supplier_id="1",
        invoice=Invoice(
            invoice_id='4711',
            invoice_date=date(2025, 1, 1),
            invoice_seller_id="1",
            invoice_seller_name="EDEKA",
            positions=[
                InvoiceItem(pos_idx=1, pos_nr="1", pos_name='Artikel',
                            pos_seller_id='1', pos_net_price=2.0, pos_total_line_amount=2.0)
            ]
        )
    )

    evt_store.add_event(evt_invoice_imported, expected_version=-1)
    evts = evt_store.readEventsByType(EvtTypes.INVOICE_IMPORTED.value)
    assert len(evts) == 1

    builder.run()
    data_store = SqliteDataStore(conn_mgr)
    docs: List[Document] = data_store.get_doc_list()
    assert len(docs) == 1

    teardown(db_file, conn_mgr)

def test_order_confirmations():
    """Testet, ob Bestellbestätigungen (EDEKA, PAXAN) verarbeitet werden"""

    db_file = Path('testdb.sqlite')
    conn_mgr = setup(db_file)
    status_queue = SimpleQueue()
    builder = RmDocumentListBuilder(conn_mgr, status_queue)
    evt_store = SqliteEventStore(conn_mgr)

    evt_invoice_imported = event_factory.orderconfirmation_imported_event(
        order_conf=OrderConfirmation(
            suppl_id='2',
            suppl_name='Paxan',
            order_confirm_id='order4711',
            order_date=date(2025, 1, 1),
            positions=[]
        )
    )

    evt_store.add_event(evt_invoice_imported, expected_version=-1)
    evts = evt_store.readEventsByType(EvtTypes.ORDERCONF_IMPORTED.value)
    assert len(evts) == 1

    builder.run()
    data_store = SqliteDataStore(conn_mgr)
    docs: List[Document] = data_store.get_doc_list()
    assert len(docs) == 1

    teardown(db_file, conn_mgr)

def test_generic_invoice():
    """Testet, ob manuelle Rechnungen verarbeitet werden"""

    db_file = Path('testdb.sqlite')
    conn_mgr = setup(db_file)
    status_queue = SimpleQueue()
    builder = RmDocumentListBuilder(conn_mgr, status_queue)
    evt_store = SqliteEventStore(conn_mgr)

    evt_invoice_imported = event_factory.generic_invoice_imported_event(
        doc=event_factory.GenericInvoice(
            suppl_id='99',
            suppl_name='Sonstwer',
            invoice_id='RENR4711',
            invoice_date=date(2025, 3, 4),
            positions=[]
        )
    )

    evt_store.add_event(evt_invoice_imported, expected_version=-1)
    evts = evt_store.readEventsByType(EvtTypes.GENERIC_INVOICE_IMPORTED.value)
    assert len(evts) == 1

    builder.run()
    data_store = SqliteDataStore(conn_mgr)
    docs: List[Document] = data_store.get_doc_list()
    assert len(docs) == 1

    teardown(db_file, conn_mgr)

def test_generic_order():
    """Testet, ob manuelle Bestellungen verarbeitet werden"""

    db_file = Path('testdb.sqlite')
    conn_mgr = setup(db_file)
    status_queue = SimpleQueue()
    builder = RmDocumentListBuilder(conn_mgr, status_queue)
    evt_store = SqliteEventStore(conn_mgr)

    evt_invoice_imported = event_factory.generic_order_imported_event(
        doc=event_factory.GenericOrder(
            suppl_id='99',
            suppl_name='Sonstwer',
            order_id='ORDER0815',
            order_date=date(2025, 3, 8),
            positions=[]
        )
    )

    evt_store.add_event(evt_invoice_imported, expected_version=-1)
    evts = evt_store.readEventsByType(EvtTypes.GENERIC_ORDER_IMPORTED.value)
    assert len(evts) == 1

    builder.run()
    data_store = SqliteDataStore(conn_mgr)
    docs: List[Document] = data_store.get_doc_list()
    assert len(docs) == 1

    teardown(db_file, conn_mgr)