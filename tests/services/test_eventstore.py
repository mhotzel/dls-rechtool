
from pathlib import Path
from services.event_store.sqlite_eventstore import SqliteEventStore
from services.sqlite_conn_manager import SqliteConnectionManager
from services.event_store.event import Event
from uuid import UUID, uuid1

def test_conn_manager():

    sqlite_db_file = Path('testdb.sqlite')
    sqlite_db_file.unlink(missing_ok=True)

    mgr = SqliteConnectionManager()
    mgr.dbFile = sqlite_db_file
    conn1 = mgr.get_connection()
    conn2 = mgr.get_connection()
    assert conn1 is not None
    assert conn2 is not None
    assert conn1 == conn2

    mgr.close_connection()
    sqlite_db_file.unlink(missing_ok=True)

def test_sqlite_evtstore_available():

    sqlite_db_file = Path('testdb.sqlite')
    sqlite_db_file.unlink(missing_ok=True)

    mgr = SqliteConnectionManager()
    mgr.dbFile = sqlite_db_file
    
    evt_store = SqliteEventStore(mgr)
    assert evt_store is not None

    evt = Event.createEvent(
        id=uuid1(),
        subject="subject",
        type="supplier.onboarded",
        data="Daten"
    )
    evt_store.add_event(evt=evt, expected_version=None)
    mgr.close_connection()
    sqlite_db_file.unlink(missing_ok=True)
