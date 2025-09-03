import atexit
from typing import Sequence
from services.event_store.eventstore import ConcurrencyError, EventStore
from services.event_store.event import Event
import sqlite3
import uuid
from threading import Lock, local, get_ident

SQL = ["""
CREATE TABLE IF NOT EXISTS events_t (
    position INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL,
	evt_id TEXT NOT NULL UNIQUE,
	specversion TEXT NOT NULL,
	source TEXT NOT NULL,
	type TEXT NOT NULL,
	subject TEXT,
	datacontenttype TEXT,
	timestamp TEXT,
	data TEXT
);
""", """
CREATE UNIQUE INDEX IF NOT EXISTS idx_subject_version ON events_t(subject, version);
""", """
CREATE INDEX IF NOT EXISTS idx_type ON events_t(type);
""", """
CREATE INDEX IF NOT EXISTS idx_subject ON events_t(subject);
""", """ 
CREATE INDEX IF NOT EXISTS idx_timestamp ON events_t(timestamp);
"""]


def dict_factory(cursor: sqlite3.Cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


class ThreadSafeConnectionManager:
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
        self._migrate()

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

    def _migrate(self):
        """Prüft, ob die Datenbank vorhanden ist und legt diese an, wenn nicht"""
        conn = self.get_connection()
        for stmt in SQL:
            conn.execute(stmt)

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
        conn: sqlite3.Connection = getattr(self._all_conns_lock, "conn", None)
        if conn is not None:
            try:
                conn.close()
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


class SqliteEventStore(EventStore):
    """Speichert Events in einer SQLITE3-Datenbank"""

    def __init__(self, conn_manager: ThreadSafeConnectionManager = None):
        super().__init__()
        self.conn_manager = conn_manager

    def _get_stream_version_tx(self, cursor: sqlite3.Cursor, subject):
        cursor.execute(
            "SELECT MAX(version) as max_version FROM events_t WHERE subject=?", (subject,))
        v = cursor.fetchone()['max_version']
        return int(v) if v is not None else None

    def add_event(self, evt: Event, expected_version: int | None) -> None:
        """Fuegt ein Event dem Store hinzu.
        event: Das zu speichernde Event
        expected_version:
           - None  => keine Versionsprüfung (append regardless)
           - int   => aktuelle Subject-Version MUSS == expected_version sein
                      (zur Abbildung optimistischer Concurrency; so wird verhindert, 
                      dass ein anderer Prozess zwischenzeitlich unbemerkt bereits
                      ein Event der gleichen Nummer geschrieben hat)
           - -1    => Subject MUSS neu sein (keine Events vorhanden)
        """

        insert_stmt = """
            INSERT INTO events_t 
                (version, evt_id, specversion, source, type, subject, datacontenttype, timestamp, data) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn: sqlite3.Connection = self.conn_manager.get_connection()
        cur: sqlite3.Cursor = conn.cursor()
        cur.execute('BEGIN IMMEDIATE;')

        try:
            current_version = self._get_stream_version_tx(cur, evt.subject)
            if expected_version == -1 and current_version is not None:
                raise ConcurrencyError(
                    f"Subject '{evt.subject}' existiert bereits (version={current_version}).")

            if isinstance(expected_version, int) and expected_version >= 0:
                if (current_version or 0) != expected_version:
                    raise ConcurrencyError(
                        f"Erwartete Version {expected_version}, tatsächlich {current_version or 0}."
                    )

            next_version = (current_version or 0) + 1

            conn.execute(
                insert_stmt, (
                    next_version,
                    str(evt.id),
                    evt.specversion,
                    evt.source,
                    evt.type,
                    evt.subject,
                    evt.datacontenttype,
                    evt.time.isoformat(),
                    evt.data
                )
            )

            next_version += 1
            conn.commit()

        except Exception:
            conn.rollback()
            raise

    def readEventsByType(self, evtType: str, from_position: int = 1, limit: int | None = None) -> Sequence[Event]:
        """Ermittelt alle Events zum angegebenen Event Typ.
        from_position => Ab welcher Position soll gelesen werden?
        limit         => Anzahl zu lesender Events
        """

        sql = 'SELECT * FROM events_t WHERE type = ? AND position >= ? ORDER BY position ASC'
        result: Sequence[Event] = []

        params = [evtType, from_position]
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)

        conn = self.conn_manager.get_connection()
        rs = conn.execute(sql, params).fetchall()
        for row in rs:
            evt = self._row_to_event(row)
            result.append(evt)
        return result

    def readSubject(self, subject: str, from_version: int = 1, limit: int | None = None) -> Sequence[Event]:
        """Liest alle Events mit dem uebergebenen Subject, also einen 'Stream'.
        from_version  => Ab welcher Version soll gelesen werden?
        limit         => Anzahl zu lesender Events
        """

        sql = 'SELECT * FROM events_t WHERE subject = ? AND version >= ? ORDER BY version ASC'
        result: Sequence[Event] = []

        params = [subject, from_version]
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)

        conn = self.conn_manager.get_connection()
        rs = conn.execute(sql, params).fetchall()
        for row in rs:
            evt = self._row_to_event(row)
            result.append(evt)
        return result

    def readEventById(self, id: uuid.UUID) -> Event:
        """Liefert das Event mit einer bestimmten ID"""

        sql = 'SELECT * FROM events_t WHERE evt_id = ?'

        conn = self.conn_manager.get_connection()
        row = conn.execute(sql, (str(id),)).fetchone()
        evt = self._row_to_event(row)
        return evt

    @staticmethod
    def _row_to_event(row) -> Event:
        evt = Event(
            id=uuid.UUID(row['evt_id']),
            position=row['position'],
            version=row['version'],
            specversion=row['specversion'],
            datacontenttype=row['datacontenttype'],
            source=row['source'],
            type=row['type'],
            subject=row['subject'],
            time=row['timestamp'],
            data=row['data']
        )
        return evt
