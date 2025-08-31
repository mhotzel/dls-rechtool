
from datetime import date
from typing import List
from pydantic import BaseModel


class OrderItem(BaseModel):
    idx: int
    seller_assigned_id: str
    global_id: str | None
    name: str
    quantity: float
    unitcode: str
    packaging_quantity: float
    price: float
    total_line_amount: float

class OrderConfirmation(BaseModel):
    seller_id: str
    order_confirm: str
    order_date: date
    positions: List[OrderItem] | None