from pydantic import BaseModel


class Supplier(BaseModel):
    """Ein Lieferant"""
    suppl_id: str
    suppl_name: str
    seller_id: str | None

    def __str__(self):
        if self.seller_id:
            return f"{self.suppl_name}    ({self.suppl_id} / {self.seller_id})"
        else:
            return f"{self.suppl_name}    ({self.suppl_id})"
