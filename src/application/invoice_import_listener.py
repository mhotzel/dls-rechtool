

from application.app_event import AppEvent, Listener


class InvoiceImportListener(Listener):
    """Startet den Import einer Rechnung"""

    def process(self, event: AppEvent) -> None:
        """Verarbeitet das Event"""
        if not event.evt_type == 'import-invoice':
            return
        
        print(f"Ich starte nun die Oberfläche zum Import der Rechnung für '{event.evt_data}'")
