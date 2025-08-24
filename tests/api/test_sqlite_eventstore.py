import uuid
from api.event import Event
import os
from api.sqlite_eventstore import SqliteEventStore
from api.supplier_onboarded_evt import SupplierOnboardedEvent


def testWriteToEventStore():
    """Testet, ob in den Event Store geschrieben werden kann"""

    dbname = "mydb.sqlite"

    try:
        os.remove(dbname)
    except FileNotFoundError:
        pass

    evtStore = SqliteEventStore(
        dbfile=dbname
    )

    evt=Event.createEvent(id=uuid.uuid1(), subject='testevent', type='supplier.onboarded')
    soe = SupplierOnboardedEvent(suppl_id='1', suppl_name='EDEKA Ösi', seller_id='20023')
    evt.data = soe.model_dump_json()
    evtStore.add_event(evt=evt, expected_version=evtStore.EXPECTED_VERSION_NEW)

    evts_loaded = evtStore.readEventsByType('supplier.onboarded')
    assert len(evts_loaded) == 1
    assert evts_loaded[0].id == evt.id
    assert evts_loaded[0].data == soe.model_dump_json()
    
    evt3 = evtStore.readEventById(evt.id)
    assert evt.id == evt3.id
    assert evt3.data == soe.model_dump_json()

    evtStore.close()

    try:
        # os.remove(dbname)
        pass
    except FileNotFoundError:
        pass
