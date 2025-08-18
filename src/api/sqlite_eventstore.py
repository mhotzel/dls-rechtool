import json
from api.eventstore import EventStore, BaseEvent
import sqlite3
from contextlib import closing

SQL = ["""
CREATE TABLE IF NOT EXISTS events_t (
	evt_id TEXT NOT NULL PRIMARY KEY,
	specversion TEXT NOT NULL,
	source TEXT NOT NULL,
	type TEXT NOT NULL,
	subject TEXT,
	datacontenttype TEXT,
	timestamp TEXT,
	data TEXT
);
""", """
CREATE INDEX IF NOT EXISTS idx_type ON events_t(type);
""", """
CREATE INDEX IF NOT EXISTS idx_subject ON events_t(subject);
""", """ 
CREATE INDEX IF NOT EXISTS idx_timestamp ON events_t(timestamp);
"""]


class SqliteEventStore(EventStore):
    """Speichert Events in einer SQLITE3-Datenbank"""

    def __init__(self, dbfile: str):
        super().__init__()
        self.dbfile = dbfile
        self._createDb()

    def _createDb(self):
        """Prüft, ob die Datenbank vorhanden ist und legt diese an, wenn nicht"""
        with closing(sqlite3.connect(self.dbfile)) as conn:
            for stmt in SQL:
                conn.execute(stmt)

    def save_event(self, evt: BaseEvent):
        """Stores an Event"""
        evt = evt.to_dict()

        insert_stmt = """
INSERT INTO events_t 
    (evt_id, specversion, source, type, subject, datacontenttype, timestamp, data) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""
        with closing(sqlite3.connect(self.dbfile, autocommit=False)) as conn:
            conn.execute(
                insert_stmt, (
                    evt['id'],
                    evt['specversion'],
                    evt['source'],
                    evt['type'],
                    evt['subject'],
                    evt['datacontenttype'],
                    evt['time'],
                    json.dumps(evt['data'])
                )
            )

            conn.commit()
