
from typing import Sequence

from domain.suppliers import Supplier
from domain.invoice_item import InvoiceItem


class InvoiceAlreadyImportedException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ImportXInvoiceCmd:
    """Importiert die Daten einer X-Rechnung"""

    def __init__(self, invoices_items: Sequence[InvoiceItem], pos) -> Supplier:
        pass

    def __call__(self) -> Supplier:
        pass
