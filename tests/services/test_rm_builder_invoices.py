
from datetime import datetime, timezone
import json
from pathlib import Path
from sqlite3 import Cursor
from typing import Mapping
import uuid
from services.event_store.event import Event
from services.event_store.sqlite_eventstore import SqliteEventStore
from services.rm_builder.rm_builder_prod_prices import RmProductListBuilder
from services.rm_builder.rm_builder_supplier import ReadModelSupplierBuilder
from services.sqlite_conn_manager import SqliteConnectionManager


data_order_confirm_edeka1 = """
{
    "suppl_id": "1",
    "suppl_name": "EDEKA",
    "order_confirm": "E6642262241230090822",
    "order_date": "2025-01-07",
    "positions": [
        {
            "idx": 1,
            "seller_assigned_id": "2969328001",
            "global_id": "4104420024694",
            "name": "Bio Alna.Feigen 250g",
            "quantity": 1.0,
            "unitcode": "KOA",
            "packaging_quantity": 6.0,
            "price": 3.943,
            "total_line_amount": 23.658
        },
        {
            "idx": 2,
            "seller_assigned_id": "167101004",
            "global_id": null,
            "name": "B.L.Bergbauern-Butter 250g",
            "quantity": 1.0,
            "unitcode": "KOB",
            "packaging_quantity": 16.0,
            "price": 2.497,
            "total_line_amount": 39.952
        }
	]
}
"""

data_order_confirm_edeka2 = """
{
    "suppl_id": "1",
    "suppl_name": "EDEKA",
    "order_confirm": "E6642262250812085651",
    "order_date": "2025-08-14",
    "positions": [
        {
            "idx": 2255,
            "seller_assigned_id": "2346796003",
            "name": "Paulaner Spezi 0,33l DPG",
            "quantity": 1.0,
            "unitcode": "KOA",
            "packaging_quantity": 24.0,
            "price": 0.586,
            "total_line_amount": 14.064
        },
        {
            "idx": 2256,
            "seller_assigned_id": "4483571000",
            "global_id": "4104760411864",
            "name": "Black Forest Still 0,7l MW",
            "quantity": 2.0,
            "unitcode": "KOA",
            "packaging_quantity": 12.0,
            "price": 0.405,
            "total_line_amount": 9.72
        },
        {
            "idx": 2257,
            "seller_assigned_id": "402567000",
            "global_id": "4001325012385",
            "name": "Naturparkquelle Medium 0,7l MW",
            "quantity": 4.0,
            "unitcode": "KOA",
            "packaging_quantity": 12.0,
            "price": 0.229,
            "total_line_amount": 10.992
        }
    ]
}
"""

data_invoice_weber = """
{
    "invoice_id": "23845",
    "invoice_date": "2025-07-31",
    "invoice_seller_id": "1",
    "invoice_seller_name": "Bäckerei Weber GmbH",
    "invoice_seller_globalid": null,
    "positions": [
        {
            "pos_idx": 1,
            "pos_nr": "1",
            "pos_global_id": null,
            "pos_seller_id": "1701",
            "pos_name": "Urweizen-Brot",
            "pos_gross_price": 3.23,
            "pos_gross_quantity": 1.0,
            "pos_gross_unitcode": "H87",
            "pos_net_price": 3.23,
            "pos_net_quantity": 1.0,
            "pos_net_unitcode": "H87",
            "pos_billed_quantity": 2.0,
            "pos_billed_unitcode": "H87",
            "pos_tax_percent": 7.0,
            "pos_total_line_amount": 6.46
        },
        {
            "pos_idx": 2,
            "pos_nr": "2",
            "pos_global_id": "32487234",
            "pos_seller_id": "1700",
            "pos_name": "Urweizen-Brot2",
            "pos_gross_price": 3.23,
            "pos_gross_quantity": 1.0,
            "pos_gross_unitcode": "H87",
            "pos_net_price": 3.23,
            "pos_net_quantity": 1.0,
            "pos_net_unitcode": "H87",
            "pos_billed_quantity": 1.0,
            "pos_billed_unitcode": "H87",
            "pos_tax_percent": 7.0,
            "pos_total_line_amount": 3.23
        }
    ]
}
"""

data_invoice_kurz = """
{
    "invoice_id": "106955",
    "invoice_date": "2025-07-26",
    "invoice_seller_id": "1",
    "invoice_seller_name": "Metzgerei Kurz GmbH",
    "invoice_seller_globalid": "4031339000009",
    "positions": [
        {
            "pos_idx": 1,
            "pos_nr": "1",
            "pos_global_id": "4031339005240",
            "pos_seller_id": "524",
            "pos_name": "Remstalsalami QZBW, 100g/Pack, geschnitten, atmos SB",
            "pos_gross_price": 1.25,
            "pos_gross_quantity": null,
            "pos_gross_unitcode": null,
            "pos_net_price": 1.25,
            "pos_net_quantity": null,
            "pos_net_unitcode": null,
            "pos_billed_quantity": 10.0,
            "pos_billed_unitcode": "C62",
            "pos_tax_percent": 7.0,
            "pos_total_line_amount": 12.5
        },
        {
            "pos_idx": 2,
            "pos_nr": "2",
            "pos_global_id": "4031339006636",
            "pos_seller_id": "663",
            "pos_name": "Hinterschinken QZBW, 125g/Pack, geschnitten, atmos SB",
            "pos_gross_price": 1.76,
            "pos_gross_quantity": null,
            "pos_gross_unitcode": null,
            "pos_net_price": 1.76,
            "pos_net_quantity": null,
            "pos_net_unitcode": null,
            "pos_billed_quantity": 5.0,
            "pos_billed_unitcode": "C62",
            "pos_tax_percent": 7.0,
            "pos_total_line_amount": 8.8
        }
    ]
}
"""

data_invoice_edeka = """
{
    "invoice_id": "3805244081",
    "invoice_date": "2025-08-14",
    "invoice_seller_id": "1",
    "invoice_seller_name": "EDEKA Foodservice Stiftung & Co.KG",
    "invoice_seller_globalid": null,
    "positions": [
        {
            "pos_idx": 1,
            "pos_nr": "10",
            "pos_global_id": "4066600103431",
            "pos_seller_id": "2346796003",
            "pos_name": "Paulaner Spezi 0,33l DPG",
            "pos_gross_price": 0.586,
            "pos_gross_quantity": 24.0,
            "pos_gross_unitcode": "STC",
            "pos_net_price": 0.586,
            "pos_net_quantity": null,
            "pos_net_unitcode": null,
            "pos_billed_quantity": 1.0,
            "pos_billed_unitcode": "XCT",
            "pos_tax_percent": 19.0,
            "pos_total_line_amount": 14.06
        },
        {
            "pos_idx": 2,
            "pos_nr": "20",
            "pos_global_id": "407",
            "pos_seller_id": "1369169007",
            "pos_name": "Pfand DPG 24x0,25=6,00 A",
            "pos_gross_price": 6.0,
            "pos_gross_quantity": 1.0,
            "pos_gross_unitcode": "XCT",
            "pos_net_price": 6.0,
            "pos_net_quantity": null,
            "pos_net_unitcode": null,
            "pos_billed_quantity": 1.0,
            "pos_billed_unitcode": "XCT",
            "pos_tax_percent": 19.0,
            "pos_total_line_amount": 6.0
        },
        {
            "pos_idx": 71,
            "pos_nr": "600",
            "pos_global_id": "35709",
            "pos_seller_id": "4010503003",
            "pos_name": "THM Kommissionierkiste grau 60x40x20cm",
            "pos_gross_price": 5.0,
            "pos_gross_quantity": 3.0,
            "pos_gross_unitcode": "XCT",
            "pos_net_price": 5.0,
            "pos_net_quantity": null,
            "pos_net_unitcode": null,
            "pos_billed_quantity": 3.0,
            "pos_billed_unitcode": "XCT",
            "pos_tax_percent": 19.0,
            "pos_total_line_amount": 15.0
        },
        {
            "pos_idx": 72,
            "pos_nr": "601",
            "pos_global_id": "35709",
            "pos_seller_id": "4010503003",
            "pos_name": "THM Kommissionierkiste grau 60x40x20cm",
            "pos_gross_price": 5.0,
            "pos_gross_quantity": 2.0,
            "pos_gross_unitcode": "XCT",
            "pos_net_price": 5.0,
            "pos_net_quantity": null,
            "pos_net_unitcode": null,
            "pos_billed_quantity": 2.0,
            "pos_billed_unitcode": "XCT",
            "pos_tax_percent": 19.0,
            "pos_total_line_amount": -10.0
        }
    ]
}
"""


def test_initial_setup():
    """Testet den initialen Aufbau der Tabellen des ReadModels"""

    db_file = Path('testdb.sqlite')
    ab_path = db_file.absolute()
    db_file.unlink(missing_ok=True)

    conn_mgr = SqliteConnectionManager()
    conn_mgr.dbFile = str(db_file)
    rmw = RmProductListBuilder(conn_mgr=conn_mgr)
    rmw._initial_setup()

    conn = conn_mgr.get_connection()
    sql1 = 'SELECT COUNT(*) as anz FROM checkpoints_t'
    sql2 = 'SELECT COUNT(*) as anz FROM rm_product_list_t'

    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 0

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 0

    conn_mgr.close_all_connections()
    db_file.unlink(missing_ok=True)

def test_rm_invoices_weber():
    """Testet die Verarbeitung von Rechnungen"""

    db_file = Path('testdb.sqlite')
    ab_path = db_file.absolute()
    db_file.unlink(missing_ok=True)

    conn_mgr = SqliteConnectionManager()
    conn_mgr.dbFile = str(db_file)
    conn = conn_mgr.get_connection()
    conn_mgr.close_connection()
    evt_store = SqliteEventStore(conn_mgr)

    evt = Event.createEvent(
        id=uuid.uuid1(),
        subject=f"invoice-5-23845",
        type='invoice.imported',
        data=data_invoice_weber
    )

    evt_store.add_event(evt=evt, expected_version=-1)

    rmw = RmProductListBuilder(conn_mgr=conn_mgr)
    rmw._initial_setup()

    conn = conn_mgr.get_connection()
    sql1 = 'SELECT COUNT(*) as anz FROM checkpoints_t'
    sql2 = 'SELECT COUNT(*) as anz FROM rm_product_list_t'

    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 0

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 0
    conn_mgr.close_connection()
    rmw.run()

    conn = conn_mgr.get_connection()
    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 1

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 2

    conn_mgr.close_all_connections()
    db_file.unlink(missing_ok=True)

def test_rm_invoices_weber_edeka():
    """Testet die Verarbeitung von Rechnungen"""

    db_file = Path('testdb.sqlite')
    ab_path = db_file.absolute()
    db_file.unlink(missing_ok=True)

    conn_mgr = SqliteConnectionManager()
    conn_mgr.dbFile = str(db_file)
    conn = conn_mgr.get_connection()
    conn_mgr.close_connection()
    evt_store = SqliteEventStore(conn_mgr)

    evt = Event.createEvent(
        id=uuid.uuid1(),
        subject=f"invoice-5-23845",
        type='invoice.imported',
        data=data_invoice_weber
    )

    evt_store.add_event(evt=evt, expected_version=-1)

    rmw = RmProductListBuilder(conn_mgr=conn_mgr)
    rmw._initial_setup()

    conn = conn_mgr.get_connection()
    sql1 = 'SELECT COUNT(*) as anz FROM checkpoints_t'
    sql2 = 'SELECT COUNT(*) as anz FROM rm_product_list_t'

    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 0

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 0
    conn_mgr.close_connection()
    rmw.run()

    conn = conn_mgr.get_connection()
    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 1

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 2
    conn_mgr.close_connection()

    evt = Event.createEvent(
        id=uuid.uuid1(),
        subject=f"invoice-1-3805244081",
        type='invoice.imported',
        data=data_invoice_edeka
    )
    evt_store.add_event(evt=evt, expected_version=-1)

    rmw.run()

    conn = conn_mgr.get_connection()
    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 1

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 5
    conn_mgr.close_connection()

    conn_mgr.close_all_connections()
    db_file.unlink(missing_ok=True)

def test_rm_orderconf_edeka():
    """Testet die Verarbeitung von Bestellbestätigungen von EDEKA"""

    db_file = Path('testdb.sqlite')
    ab_path = db_file.absolute()
    db_file.unlink(missing_ok=True)

    conn_mgr = SqliteConnectionManager()
    conn_mgr.dbFile = str(db_file)
    conn = conn_mgr.get_connection()
    conn_mgr.close_connection()
    evt_store = SqliteEventStore(conn_mgr)

    evt = Event.createEvent(
        id=uuid.uuid1(),
        subject=f"orderconfirmation-1-E6642262250724121654",
        type='orderconf.imported',
        data=data_order_confirm_edeka1
    )

    evt_store.add_event(evt=evt, expected_version=-1)

    rmw = RmProductListBuilder(conn_mgr=conn_mgr)
    rmw._initial_setup()

    conn = conn_mgr.get_connection()
    sql1 = 'SELECT COUNT(*) as anz FROM checkpoints_t'
    sql2 = 'SELECT COUNT(*) as anz FROM rm_product_list_t'

    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 0

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 0
    conn_mgr.close_connection()
    rmw.run()

    conn = conn_mgr.get_connection()
    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 1

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 2

    conn_mgr.close_connection()

    evt = Event.createEvent(
        id=uuid.uuid1(),
        subject=f"orderconfirmation-1-E6642262250812085651",
        type='orderconf.imported',
        data=data_order_confirm_edeka2
    )

    evt_store.add_event(evt=evt, expected_version=-1)
    rmw.run()
    
    conn = conn_mgr.get_connection()
    res = conn.execute(sql1).fetchone()
    assert res['anz'] == 1

    res = conn.execute(sql2).fetchone()
    assert res['anz'] == 5
    
    # db_file.unlink(missing_ok=True)
