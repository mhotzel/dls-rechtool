
from abc import abstractmethod
from datetime import date
from typing import List, Protocol

from pydantic import BaseModel


class Product(BaseModel):
    """Ein Artikel samt Herkunft"""
    suppl_id: str
    suppl_name: str | None = None
    issue_type: str
    issue_id: str
    issue_date: date
    seller_assigned_id: str
    global_id: str | None=None
    name: str | None = None
    price: float


class DataStore(Protocol):

    @abstractmethod
    def get_product_list(self) -> List[Product]:
        """Liefert die Liste der Artikel mit Einzelpreisen"""
