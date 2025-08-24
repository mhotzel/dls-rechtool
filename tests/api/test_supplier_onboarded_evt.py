import uuid
from api.event import Event
from api import supplier_onboarded_evt


def test_supplierOnboardedEvent():

    id: uuid.UUID = uuid.uuid1()
    subject: str = "supplier-id=1"
    evt_type: str = 'supplier.onboarded'
    suppl_id: str = '1'
    suppl_name: str = 'TestSuppl'
    seller_id: str = "2003"
    data: str

    evt: Event = supplier_onboarded_evt.createEvent(
        id=id,
        suppl_id='1',
        suppl_name=suppl_name,
        seller_id=seller_id
    )

    assert evt is not None
    assert evt.id== id
    assert evt.time is not None
    assert evt.subject == 'supplier-id=1'
    assert evt.type == evt_type
    assert type(evt.data) == str

    suppl = supplier_onboarded_evt.SupplierOnboardedEvent.model_validate_json(evt.data)
    assert suppl.suppl_id == suppl_id
    assert suppl.suppl_name == suppl_name
    assert suppl.seller_id == seller_id