from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy, QFrame

from application.application_context import ApplicationContext


class LeftBar(QFrame):
    def __init__(self, parent, appContext: ApplicationContext):
        super().__init__(parent, lineWidth=1)
        self.appContext = appContext
        self._buildUi()

    def _buildUi(self):
        #self.setFixedWidth(200)
        _layout = QVBoxLayout()
        self.btn_edeka = QPushButton("EDEKA-Rechnung importieren")
        self.btn_edeka.clicked.connect(
            lambda: self.appContext.import_invoice("EDEKA"))
        self.btn_kurz = QPushButton("Kurz-Rechnung importieren")
        self.btn_kurz.clicked.connect(
            lambda: self.appContext.import_invoice("Kurz", bla="blubb"))
        # self.button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        _layout.addWidget(self.btn_edeka)
        _layout.addWidget(self.btn_kurz)
        _layout.addStretch(1)
        self.setLayout(_layout)
