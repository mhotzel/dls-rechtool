import atexit
import sqlite3
from threading import Lock, get_ident, local

def dict_factory(cursor: sqlite3.Cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class SqliteConnectionManager:
    """Verwaltet eine thread-lokale SQLite-Verbindung."""

    def __init__(self):
        # map der thread_id zur conn (für sauberes Schließen)
        self._all_conns = {}
        self._all_conns_lock = Lock()
        self._thread_local = local()
        self.__dbFile = None
        atexit.register(self.close_all_connections)

    @property
    def dbFile(self) -> str:
        return self.__dbFile

    @dbFile.setter
    def dbFile(self, dbf: str) -> None:
        self.__dbFile = dbf
        """Schließt alle bestehenden Verbindungen und legt die DB ggf. an."""
        self.close_all_connections()

    def get_connection(self) -> sqlite3.Connection:
        """Liefert die thread-lokale Verbindung; erzeugt sie bei Bedarf."""
        conn = getattr(self._thread_local, "conn", None)
        if conn is None:
            conn = self._new_connection()
            self._thread_local.conn = conn
            self._thread_local.conn.row_factory = dict_factory
            with self._all_conns_lock:
                self._all_conns[get_ident()] = conn
        return conn

    def _new_connection(self) -> sqlite3.Connection:
        """Erzeugt eine neue DB-Verbindung mit sinnvollen Defaults."""
        conn = sqlite3.connect(
            self.__dbFile,
            timeout=30.0,                      # Wartezeit bei Locks
            detect_types=sqlite3.PARSE_DECLTYPES,
            isolation_level=None               # autocommit; oder setze z.B. "DEFERRED"
        )
        # sinnvolle Defaults für paralleles Lesen/Schreiben
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def close_connection(self) -> None:
        """Schließt die Verbindung des aktuellen Threads (falls vorhanden)."""
        conn: sqlite3.Connection = getattr(self._thread_local, "conn", None)
        if conn is not None:
            try:
                conn.close()
            except Exception as e:
                print(e)
            finally:
                self._thread_local.conn = None
                with self._all_conns_lock:
                    self._all_conns.pop(get_ident(), None)

    def close_all_connections(self):
        """Schließt alle Verbindungen, insb. beim Beenden des Prozesses (atexit) und wenn sich die DB ändert."""
        with self._all_conns_lock:
            conns = list(self._all_conns.values())
            self._all_conns.clear()

        c: sqlite3.Connection
        for c in conns:
            try:
                c.close()
            except Exception:
                pass