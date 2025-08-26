
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QGridLayout, QWidget, QLineEdit, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from services.config_service import ConfigService


class SetupWindow(QMainWindow):

    def __init__(self, configService: ConfigService, firstStart: bool = False):
        super().__init__()
        self.first_start: bool = firstStart
        self.configService = configService
        self.__setDesign()
        self.setWindowTitle(
            'DLS - Rechnungs- und Lieferantedatenerfassung - Initiales Setup')
        self.__build_ui()

    def __setDesign(self) -> None:
        """Setzt die StyleSheets usw"""
        self.setStyleSheet("""
            QWidget { background: #f3f3f3; font-family: calibri, arial, helvetica, sans-serif; font-size: 14px; }
            QPushButton { padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px; background-color: rgb(142,190,68); font-weight: bold; color: white; }
            QPushButton:hover { background: #eaeaea; color: black; }
            QLineEdit {background-color: white; padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px; }
        """)

    def __build_ui(self) -> None:
        self.setCentralWidget(QWidget())
        _layout = QGridLayout(self.centralWidget())
        self.centralWidget().setLayout(_layout)

        # _layout = QGridLayout(self)
        # self.setLayout(_layout)
        self.txtPathToDb = QLineEdit("leer")
        self.txtPathToDb.setReadOnly(True)
        self.txtPathToDb.setDisabled(True)
        self.btnSelectExistingFile = QPushButton("Bestehende Datei auswählen")
        self.btnSelectFolderForNewFile = QPushButton(
            "Pfad für neu anzulegende Datenbankdatei auswählen")

        _layout.addWidget(self.txtPathToDb, 0, 0, 1, 2)
        _layout.addWidget(self.btnSelectExistingFile, 1, 0,
                          1, 1, Qt.AlignmentFlag.AlignHCenter)
        _layout.addWidget(self.btnSelectFolderForNewFile, 1,
                          1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.btnSelectFolderForNewFile.clicked.connect(
            self.__selectFolderForNewFile)
        self.btnSelectExistingFile.clicked.connect(self.__selectDbFile)

    def __selectFolderForNewFile(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, caption="Ordner für Datenbankdatei auswählen", dir=str(Path().home()))
        if len(folder) > 0 and folder is not None:
            db_file_path = Path(folder).joinpath('dlsrech.sqlite')
            self.txtPathToDb.setText(str(db_file_path))
            self.setDbFile(self.txtPathToDb.text())
        else:
            self.__showWarnIncompleteConfig()

    def __selectDbFile(self) -> None:
        file, _ = QFileDialog.getOpenFileName(self, "Datenbankdatei auswählen", dir=str(
            Path().home()), filter='Datenbank-Datei (*.sqlite *.db)')
        if len(file) > 0 and file is not None:
            self.txtPathToDb.setText(file)
            self.setDbFile(self.txtPathToDb.text())
        else:
            self.__showWarnIncompleteConfig()

    def setDbFile(self, dbFileName: str) -> bool:
        """Schreibt die Konfiguration in die Konfigurationsdatei.
        wird True zurückgegeben, muss die Anwendung neu gestartet werden.
        """

        old_file = self.configService.getDatabaseFilePath()
        new_file = Path(dbFileName)
        self.configService.saveDatabaseFilePath(new_file)

        QMessageBox.information(
            self,
            "Konfiguration wurde erfolgreich angelegt",
            f"Die Konfiguration wurde erfolgreich gespeichert."
        )

        isNewFile = False
        if old_file != new_file and not self.first_start:
            isNewFile = True
            QMessageBox.warning(
                self,
                "Neustart erforderlich",
                f"Die Anwendung muss neu gestartet werden"
            )

        self.close()
        return isNewFile

    def __showWarnIncompleteConfig(self) -> None:
        QMessageBox.warning(
            self,
            "Konfiguration ist nicht vollständig!",
            "Es wurde keine Datenbankdatei ausgewählt und in der Konfiguration gespeichert!\nDamit ist die Anwendung nicht benutzbar und wird beendet"
        )

    def show(self):
        pfad = str(self.configService.getDatabaseFilePath())
        self.txtPathToDb.setText(pfad)
        return super().show()
