from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy, QFrame


class LeftBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent, lineWidth=1)
        self._buildUi()

    def _buildUi(self):
        #self.setFixedWidth(200)
        _layout = QVBoxLayout()
        self.button = QPushButton("Drück mich")
        self.button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button2 = QPushButton("Drück mich auch mal")
        _layout.addWidget(self.button)
        _layout.addWidget(self.button2)
        self.setLayout(_layout)
        _layout.addStretch(1)