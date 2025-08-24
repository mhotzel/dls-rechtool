
import uuid
from api.event import Event

def test_baseevent():

    id :uuid.UUID = uuid.uuid1()
    subject: str = "testsub=1"
    evt_type: str = "evt.type"
    data = "{'name': 'mat', 'age': 52}"

    evt = Event.createEvent(id=id, subject=subject, type=evt_type)
    evt.data = data

    assert evt.id == id
    assert evt.datacontenttype == 'application/json'
    assert evt.source == 'dorfladen-schlichten.de/dlrech/events'
    assert evt.type == evt_type
    assert evt.data == data

    evt_json = evt.model_dump_json(by_alias=True)
    assert evt_json is not None
    
    evt2 = Event.model_validate_json(evt_json)
    assert evt2 == evt