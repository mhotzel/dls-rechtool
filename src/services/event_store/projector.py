
import sqlite3


class SupplierProjector:
    """Überwacht die Events, die die Lieferanten ebtreffen und aktualisiert die Projektionen, also die Lesemodelle"""

    def __init__(self, dbfile: str):
        super().__init__()
        self.dbfile = dbfile
        self.name = 'suppliers'
        self.conn = sqlite3.connect(dbfile, isolation_level=None)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")

        self._init_schema()

        self.handlers = {
            'supplier.onboarded': self.supplier_onboarded,
            'supplier.ofboarded': self.supplier_onboarded
        }

    def supplier_onboarded(self):
        """Reagiert auf die Aufnahme eines neuen Lieferanten"""

    def supplier_offboarded(self):
        """Reagiert auf das Ausphasen eines Lieferanten"""
        
    
    def _init_schema(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS projection_checkpoints_t (
          name TEXT PRIMARY KEY,
          last_position INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS rm_invoice_summary_t (
          suppl_id       TEXT PRIMARY KEY,
          supplier_name  TXT NOT NULL,
          seller_id     TEXT NOT NULL,
          updated       TEXT
        );
        """)

    def _get_last_position(self) -> int:
        cur = self.conn.execute("SELECT last_position FROM projection_checkpoints WHERE name=?", (self.name,))
        row = cur.fetchone()
        return int(row[0]) if row else 0
    
    def _set_last_position(self, pos: int):
        self.conn.execute("""
            INSERT INTO projection_checkpoints(name, last_position)
            VALUES(?, ?)
            ON CONFLICT(name) DO UPDATE SET last_position=excluded.last_position
        """, (self.name, pos))
        