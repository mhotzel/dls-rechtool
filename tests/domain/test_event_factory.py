
from domain.event_factory import build_stream_id


def test_build_stream_id():

    aggregate: str = "orders"
    comp1 = 'Customer-234/3'
    comp2 = 'bestNr4711/2'

    result = build_stream_id(aggregate, comp1,  comp2)

    assert result == "orders/customer-234%2F3/bestnr4711%2F2"


