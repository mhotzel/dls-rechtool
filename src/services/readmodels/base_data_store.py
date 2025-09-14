
from abc import abstractmethod
from datetime import date
from typing import List, Protocol

from pydantic import BaseModel


class Supplier(BaseModel):
    """Ein Lieferant"""
    suppl_id: str
    suppl_name: str
    seller_id: str | None = None


class Document(BaseModel):
    subject: str
    doc_date: date
    doc_type: str
    doc_id: str
    suppl_id: str
    suppl_name: str
    doc_state: str | None = None


class Product(BaseModel):
    """Ein Artikel samt Herkunft"""
    suppl_id: str
    suppl_name: str | None = None
    issue_type: str
    issue_id: str
    issue_date: date
    seller_assigned_id: str
    global_id: str | None = None
    name: str | None = None
    price: float


class DataStore(Protocol):

    @abstractmethod
    def get_product_list(self) -> List[Product]:
        """Liefert die Liste der Artikel mit Einzelpreisen"""
        ...

    @abstractmethod
    def get_doc_list(self) -> List[Document]:
        """Liefert die Liste aller Dokumente"""
        ...

    @abstractmethod
    def get_suppliers_list(self) -> List[Supplier]:
        """Liefert die Liste aller Lieferanten"""
        ...
