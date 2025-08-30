
from datetime import date
from pydantic import BaseModel


class OrderItem(BaseModel):
    idx: int
    seller_id: str
    order_confirm: str
    pos_seller_id: str
    pos_global_id: str | None
    pos_name: str
    pos_quantity: float
    pos_unitcode: str
    pos_packaging_quantity: float
    pos_order_date: date
    pos_price: float
    pos_total_line_amount: float
