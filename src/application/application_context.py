from api.sqlite_eventstore import SqliteEventStore

class ApplicationContext:
    """Application context für das DLS Rechnungstool. Stellt alle benötigten zentralen Services bereit."""

    def __init__(self, db_path: str = "events.sqlite"):
        self.db_file = db_path
        self.__event_store = None

    @property
    def event_store(self):
        """Returns the event store instance."""
        if self.__event_store is None:
            self.__event_store = SqliteEventStore(self.db_file)

        return self.__event_store

    def import_invoice(self, supplier: str, **data):
        """Importiert eine Rechnung in das System."""
        print(f"Button {supplier} wurde gedrückt.")
        