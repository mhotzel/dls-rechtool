
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGroupBox

from application.app_event import AppEvent
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

        level, message = evt.evt_data.split(':', maxsplit=1)

        colors = {
            'INFO': 'green',
            'WARN': 'orange',
            'CRITICAL': 'red'
        }
        color = colors.get(level, 'black')
        self.lblMessage.setStyleSheet(f"color: {color};")

        self.lblMessage.setText(message.strip())
