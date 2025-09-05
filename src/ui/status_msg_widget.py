
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGroupBox

from application.app_event import AppEvent, LogLevel
from application.event_dispatcher import EventDispatcher

"""
Das Widget reagiert auf Events vom Typ 'status-message'
"""


class StatusMessageWidget(QGroupBox):

    def __init__(self, parent: QWidget, event_dispatcher: EventDispatcher):
        super().__init__(parent=parent, title='Statusmeldungen')
        self.event_dispatcher = event_dispatcher
        self.__build_ui()
        self.event_dispatcher.register('status-message', self.setStatus)

    def __build_ui(self) -> None:
        """Baut die Oberfläche"""
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.lblMessage = QLabel()
        layout.addWidget(self.lblMessage)
        self.lblMessage.setWordWrap(True)

    def setStatus(self, evt: AppEvent) -> None:
        """Schreibt den Status"""

        level: LogLevel = evt.evt_lvl
        message: str = evt.evt_data

        colors = {
            LogLevel.INFO: 'green',
            LogLevel.WARN: 'orange',
            LogLevel.CRITICAL: 'red'
        }
        color = colors.get(level, 'black')
        self.lblMessage.setStyleSheet(f"color: {color};")

        self.lblMessage.setText(message.strip())
