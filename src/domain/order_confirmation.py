
from datetime import date
from typing import List
from pydantic import BaseModel


class OrderConfItem(BaseModel):
    idx: int
    seller_assigned_id: str
    global_id: str | None = None
    name: str
    quantity: float | None = None
    unitcode: str | None = None
    packaging_quantity: float | None = None
    price: float
    total_line_amount: float | None = None

class OrderConfirmation(BaseModel):
    suppl_id: str
    suppl_name: str
    order_confirm_id: str
    order_date: date
    positions: List[OrderConfItem] | None = []