from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFormLayout,
    QHBoxLayout, QGroupBox, QListWidget, QFrame, QLineEdit
)


class SupplierListWidget(QGroupBox):
    """Listet die Lieferanten auf"""

    def __init__(self, parent: QWidget):
        super().__init__(title='Lieferanten pflegen', parent=parent)
        self.__build_ui()

    def __build_ui(self):
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        self.suppliersList = QListWidget(self)
        layout.addWidget(self.suppliersList)

        self.buttonGroup = QFrame(self)
        layout.addWidget(self.buttonGroup)

        btn_grp_layout = QVBoxLayout(self.buttonGroup)
        self.buttonGroup.setLayout(btn_grp_layout)
        self.btn_new = QPushButton('Neu')
        self.btn_edit = QPushButton('Ändern')
        self.btn_delete = QPushButton('Löschen')
        btn_grp_layout.addWidget(self.btn_new)
        btn_grp_layout.addWidget(self.btn_edit)
        btn_grp_layout.addWidget(self.btn_delete)
        btn_grp_layout.addStretch(1)


class SupplierEditWidget(QGroupBox):
    """Pane zur Bearbeitung eines Lieferanten"""

    def __init__(self, parent: QWidget):
        super().__init__(title='Lieferant bearbeiten', parent=parent)
        self.__build_ui()

    def __build_ui(self):
        vlayout = QVBoxLayout(self)
        self.formWidget = QWidget(self)
        form = QFormLayout(parent=self.formWidget)
        self.txt_suppl_id = QLineEdit(parent=self)
        self.txt_suppl_name = QLineEdit(parent=self)
        self.txt_seller_id = QLineEdit(parent=self)
        form.addRow('DLS-eigene Lieferanten-ID', self.txt_suppl_id)
        form.addRow('Name', self.txt_suppl_name)
        form.addRow('externe ID des Lieferanten', self.txt_seller_id)
        vlayout.addWidget(self.formWidget)

        self.btn_grp = QFrame(self)
        self.btn_cancel = QPushButton('abbrechen')
        self.btn_ok = QPushButton('Speichern')
        self.btn_grp.setLayout(QHBoxLayout())
        self.btn_grp.layout().addStretch(1)
        self.btn_grp.layout().addWidget(self.btn_cancel)
        self.btn_grp.layout().addWidget(self.btn_ok)

        vlayout.addWidget(self.btn_grp)

class SuppliersEditorWidget(QWidget):
    """Pane, welche die Anzeige und die Bearbeitungsmöglichkeit von Lieferanten kombiniert darstellt"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.__build_ui()

    def __build_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(SupplierListWidget(self))
        layout.addWidget(SupplierEditWidget(self))
        layout.addStretch(1)
