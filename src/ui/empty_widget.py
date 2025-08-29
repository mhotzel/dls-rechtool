from PySide6.QtWidgets import QWidget, QLabel, QGridLayout

class EmptyPane(QWidget):
    """Eine leere Seite für das Hauptfenster"""

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)
        self.__build_ui()

    def __build_ui(self):
        """Baut die Oberfläche"""
        self.lblMEssage = QLabel("Bitte eine Funktion links wählen")
        layout = QGridLayout(self)
        self.setLayout(layout)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(2, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)
        layout.addWidget(self.lblMEssage, 1, 1)

        self.setStyleSheet(
        """
        .QLabel { font-weight: bold; font-size: 18px;}
        """
        )
