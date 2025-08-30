from datetime import date, datetime
from pydantic import BaseModel


class InvoiceItem(BaseModel):
    """Eine Rechnung aus dem EventStore"""
    invoice_id: str
    invoice_date: date
    invoice_seller_id: str
    invoice_seller_name: str
    invoice_seller_globalid: str | None
    pos_idx: int
    pos_nr: str
    pos_global_id: str | None
    pos_seller_id: str
    pos_name: str
    pos_gross_price: float | None
    pos_gross_quantity: float | None
    pos_gross_unitcode: str | None
    pos_net_price: float
    pos_net_quantity: float | None
    pos_net_unitcode: str | None
    pos_billed_quantity: float | None
    pos_billed_unitcode: str | None
    pos_tax_percent: float | None
    pos_total_line_amount: float
