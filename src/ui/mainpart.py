from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy, QFrame

from application.application_context import ApplicationContext


class MainPart(QFrame):
    def __init__(self, parent, appContext: ApplicationContext):
        super().__init__(parent, lineWidth=1)
        self._buildUi()

    def _buildUi(self):
        _layout = QVBoxLayout()
        self.setMinimumWidth(200)
