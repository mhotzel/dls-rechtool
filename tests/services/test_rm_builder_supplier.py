
import json
from pathlib import Path
from queue import SimpleQueue
import uuid
from services.event_store.event import Event
from services.event_store.sqlite_eventstore import SqliteEventStore
from services.rm_builder.rm_builder_supplier import RmSupplierBuilder
from services.sqlite_conn_manager import SqliteConnectionManager


def test_initial_setup():
    """Testet den initialen Aufbau der Tabellen des ReadModels"""

    db_file = Path('testdb.sqlite')
    ab_path = db_file.absolute()
    db_file.unlink(missing_ok=True)

    conn_mgr = SqliteConnectionManager()
    conn_mgr.dbFile = str(db_file)
    status_queue = SimpleQueue()
    rmw = RmSupplierBuilder(conn_mgr=conn_mgr, status_queue=status_queue)
    rmw._initial_setup()

    conn = conn_mgr.get_connection()
    sql1 = 'SELECT COUNT(*) as anz FROM checkpoints_t'
    sql2 = 'SELECT COUNT(*) as anz FROM rm_suppliers_t'

    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 0

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 0

    conn_mgr.close_all_connections()
    db_file.unlink(missing_ok=True)


def test_runonce_suppliers_from_0():
    """
    Testet die initiale Verarbeitung der Lieferanten
    """

    suppliers_to_create = [
        {'suppl_id': '1', 'suppl_name': 'EDEKA', 'seller_id': '4711'},
        {'suppl_id': '2', 'suppl_name': 'Kurz', 'seller_id': '0815'},
        {'suppl_id': '3', 'suppl_name': 'Sonstige', 'seller_id': '4712'}
    ]

    db_file = Path('testdb.sqlite')
    ab_path = db_file.absolute()
    db_file.unlink(missing_ok=True)
    status_queue = SimpleQueue()

    conn_mgr = SqliteConnectionManager()
    conn_mgr.dbFile = str(db_file)
    conn = conn_mgr.get_connection()
    conn_mgr.close_connection()

    evt_store = SqliteEventStore(conn_manager=conn_mgr)

    for s in suppliers_to_create:
        evt = Event.createEvent(
            id=uuid.uuid1(),
            subject=f"supplier-{s['suppl_id']}",
            type='supplier.onboarded',
            data=json.dumps(s)
        )
        evt_store.add_event(evt=evt, expected_version=-1)

    rmw = RmSupplierBuilder(conn_mgr=conn_mgr, status_queue=status_queue)
    rmw._initial_setup()
    rmw.run()

    sql = "SELECT count(*) AS anz FROM rm_suppliers_t"
    conn = conn_mgr.get_connection()

    row = conn.execute(sql).fetchone()
    assert row
    assert row['anz'] == 3

    conn_mgr.close_all_connections()
    db_file.unlink(missing_ok=True)


def test_runonce_suppliers_from_3():
    """
    Testet die initiale Verarbeitung der Lieferanten
    """

    suppliers_to_create1 = [
        {'suppl_id': '1', 'suppl_name': 'EDEKA', 'seller_id': '4711'},
        {'suppl_id': '2', 'suppl_name': 'Kurz', 'seller_id': '0815'},
        {'suppl_id': '3', 'suppl_name': 'Sonstige', 'seller_id': '4712'}
    ]

    suppliers_to_create2 = [
        {'suppl_id': '4', 'suppl_name': 'sup4'},
        {'suppl_id': '5', 'suppl_name': 'sup5'}
    ]

    db_file = Path('testdb.sqlite')
    ab_path = db_file.absolute()
    db_file.unlink(missing_ok=True)

    conn_mgr = SqliteConnectionManager()
    conn_mgr.dbFile = str(db_file)
    conn = conn_mgr.get_connection()
    conn_mgr.close_connection()

    evt_store = SqliteEventStore(conn_manager=conn_mgr)

    for s in suppliers_to_create1:
        evt = Event.createEvent(
            id=uuid.uuid1(),
            subject=f"supplier-{s['suppl_id']}",
            type='supplier.onboarded',
            data=json.dumps(s)
        )
        evt_store.add_event(evt=evt, expected_version=-1)

    status_queue = SimpleQueue()
    rmw = RmSupplierBuilder(conn_mgr, status_queue)
    rmw._initial_setup()
    rmw.run()

    sql = "SELECT count(*) AS anz FROM rm_suppliers_t"
    conn = conn_mgr.get_connection()

    row = conn.execute(sql).fetchone()
    assert row
    assert row['anz'] == 3

    for s in suppliers_to_create2:
        evt = Event.createEvent(
            id=uuid.uuid1(),
            subject=f"supplier-{s['suppl_id']}",
            type='supplier.onboarded',
            data=json.dumps(s)
        )
        evt_store.add_event(evt=evt, expected_version=-1)

    rmw._initial_setup()
    rmw.run()

    conn = conn_mgr.get_connection()
    row = conn.execute(sql).fetchone()
    assert row
    assert row['anz'] == 5

    conn_mgr.close_all_connections()
    db_file.unlink(missing_ok=True)
