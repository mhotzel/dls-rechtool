
import os
from pathlib import Path
from uuid import uuid1
from application import db_migration
from services.event_store.event import Event
from services.event_store.sqlite_eventstore import SqliteEventStore
from services.sqlite_conn_manager import SqliteConnectionManager


def test_projection_readmodel_suppliers():

    sqlite_db_file = Path('testdb.sqlite')
    sqlite_db_file.unlink(missing_ok=True)

    mgr = SqliteConnectionManager()
    mgr.dbFile = sqlite_db_file
    db_migration.initial_setup(mgr.get_connection())

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