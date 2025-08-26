from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy, QFrame

from application.event_dispatcher import AppEvent, EventDispatcher


class LeftBar(QFrame):
    def __init__(self, parent, event_dispatcher: EventDispatcher):
        super().__init__(parent, lineWidth=1)
        self.event_dispatcher = event_dispatcher
        self._buildUi()

    def _buildUi(self):
        # self.setFixedWidth(200)
        _layout = QVBoxLayout()
        self.btn_config = QPushButton("Datenbank konfigurieren")
        self.btn_config.clicked.connect(
            lambda evt: self.event_dispatcher.send(AppEvent('config-db')))
        self.btn_edeka = QPushButton("EDEKA-Rechnung importieren")
        self.btn_edeka.clicked.connect(lambda evt: self.event_dispatcher.send(AppEvent('import-invoice', 'edeka')))
        self.btn_kurz = QPushButton("Kurz-Rechnung importieren")
        self.btn_kurz.clicked.connect(lambda evt: self.event_dispatcher.send(AppEvent('import-invoice', 'kurz')))
        # self.button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        _layout.addWidget(self.btn_config)
        _layout.addWidget(self.btn_edeka)
        _layout.addWidget(self.btn_kurz)
        _layout.addStretch(1)
        self.setLayout(_layout)
