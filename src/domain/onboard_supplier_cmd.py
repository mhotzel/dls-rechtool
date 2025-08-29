
from typing import Sequence

from domain.suppliers import Supplier


class SupplierAlreadyExistsException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class OnboardSupplierCommand:
    """Onboarded einen Lieferanten"""

    def __init__(self, suppliers: Sequence[Supplier], suppl_id: str, suppl_name: str, seller_id: str) -> Supplier:
        self.__new_supplier = Supplier(suppl_id=suppl_id, suppl_name=suppl_name, seller_id=seller_id)
        self.__existing_suppliers = suppliers

    def __call__(self) -> Supplier:
        for s in self.__existing_suppliers:
            if self.__new_supplier.suppl_id == s.suppl_id:
                raise SupplierAlreadyExistsException(f"supplier with suppl_id '{self.__new_supplier.suppl_id}' already exists")
            
        if self.__new_supplier.suppl_id is None or self.__new_supplier.suppl_id == '':
            raise ValueError(f"supplier must have a supplier-id")
        return self.__new_supplier
