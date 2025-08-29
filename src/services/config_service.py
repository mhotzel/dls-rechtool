
from contextlib import closing
import os
from pathlib import Path
from application.event_dispatcher import AppEvent


class ConfigService():
    """Verwaltet die Anwendungskonfiguration"""

    def __init__(self):
        super().__init__()
        self.config_path: Path = Path.home().joinpath('.dlsrech')
        self.config_file: Path = self.config_path.joinpath('config.ini')

    def getDatabaseFilePath(self) -> Path:
        """Ermittelt den Pfad zur Datenbank"""
        dbFileName = None

        if not self.config_path.exists():
            self.config_path.mkdir(parents=True, exist_ok=True)

        self.config_file.touch()

        with closing(open(self.config_file, encoding='utf8')) as fd:
            entries = fd.readlines()
            for entry in entries:
                if entry.startswith('dbfile='):
                    dbFileName = entry.split('=')[1]

        return Path(dbFileName) if dbFileName else ''
    
    def saveDatabaseFilePath(self, dbFileName: Path):
        """Schreibt den Pfad zur Datenbank in die Konfigurationsdatei"""
        if not self.config_path.exists():
            os.mkdir(str(self.config_path))

        with closing(open(str(self.config_file), "w", encoding='utf8')) as fd:
            fd.write(f"dbfile={str(dbFileName)}")
