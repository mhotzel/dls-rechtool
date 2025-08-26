from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy, QFrame

from application.event_dispatcher import EventDispatcher

class MainPart(QFrame):
    def __init__(self, parent, event_dispatcher: EventDispatcher):
        super().__init__(parent, lineWidth=1)
        self.event_dispatcher = event_dispatcher
        self._buildUi()

    def _buildUi(self):
        _layout = QVBoxLayout()
        self.setMinimumWidth(200)
