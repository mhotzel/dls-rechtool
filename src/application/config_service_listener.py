
from application.app_event import AppEvent
from application.event_dispatcher import Listener
from services.config_service import ConfigService
from ui.setup_window import SetupWindow


class ConfigServiceListener(Listener):
    """Lauscht auf Events zur Änderung der Konfiguration und startet die UI zur Konfigurationsdatenänderung"""

    def __init__(self, setupWin: SetupWindow):
        super().__init__()
        self.setupWin = setupWin

    def process(self, event: AppEvent) -> None:
        if not event.evt_type == 'config-db':
            return
        
        self.setupWin.show()
