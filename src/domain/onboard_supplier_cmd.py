
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
                raise SupplierAlreadyExistsException(f"Ein Lieferant mit der Nr '{self.__new_supplier.suppl_id}' existiert bereits")
            
        if self.__new_supplier.suppl_id is None or self.__new_supplier.suppl_id == '':
            raise ValueError(f"Der Lieferant muss eine eindeutige Nr. haben")
        
        if self.__new_supplier.suppl_name is None or len(self.__new_supplier.suppl_name) == 0:
            raise ValueError(f"Der Name des Lieferanten darf nicht leer sein")

        return self.__new_supplier
