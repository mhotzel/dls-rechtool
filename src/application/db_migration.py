import sqlite3


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


def initial_setup(conn: sqlite3.Connection):
    """Prüft, ob die Datenbank vorhanden ist und legt diese an, wenn nicht"""
    for stmt in SQL:
        conn.execute(stmt)
