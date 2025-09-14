
from typing import List, Union
from domain.event_factory import GenericInvoice, GenericOrder, generic_invoice_imported_event, generic_order_imported_event
from services.event_store.event import Event
from services.event_store.eventstore import EventStore
from services.readmodels.base_data_store import DataStore, Document


class ManualDocImportCmd:
    """
    Command zum Import eines manuellen Dokuments.
    Es prüft auch gegen das LeseModell ab, ob das Dokument bereits importiert wurde.
    """

    def __init__(self, data_store: DataStore, evt_store: EventStore):
        self.data_store = data_store
        self.event_store = evt_store

    def saveInvoice(self, doc: GenericInvoice) -> Event:
        evt = generic_invoice_imported_event(doc)

        if not self._find_doc(evt.subject):
            self.event_store.add_event(evt, expected_version=None)
            return evt
        raise ValueError(
            f"Das Dokument mit dem Subject '{evt.subject}' wurde bereits importiert")

    def saveOrder(self, doc: GenericOrder) -> Event:
        evt = generic_order_imported_event(doc)
        if not self._find_doc(evt.subject):
            self.event_store.add_event(evt, expected_version=None)
            return evt
        raise ValueError(
            f"Das Dokument mit dem Subject '{evt.subject}' wurde bereits importiert")

    def saveDocument(self, doc: Union[GenericInvoice, GenericOrder]) -> Event:
        if type(doc) == GenericInvoice:
            return self.saveInvoice(doc)
        else:
            return self.saveOrder(doc)

    def _find_doc(self, subject) -> bool:
        """Prüft, ob ein Dokument mit dem angegebenen Subject schon vorhanden ist"""
        docs: List[Document] = self.data_store.get_doc_list()
        for doc in docs:
            if doc.subject == subject:
                return True
        return False
