
from contextlib import closing
from os import path
import os
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QGridLayout, QWidget, QLineEdit, QPushButton, QFileDialog, QMessageBox, QApplication
from PySide6.QtGui import QIcon, QScreen
from PySide6.QtCore import Qt, QSize
from application.app_event import AppEvent
from services.config_service import ConfigService


class SetupWindow(QMainWindow):

    def __init__(self, configService: ConfigService, firstStart: bool = False):
        super().__init__()
        self.first_start: bool = firstStart
        self.configService = configService
        self.__setDesign()
        self.setWindowTitle(
            'DLS - Rechnungs- und Lieferantendatenerfassung - Initiales Setup')
        self.__build_ui()
        self.setWindowIcon(self._createIcons())

    def _createIcons(self):
        my_icon = QIcon()
        my_icon.addFile(path.join('assets', 'favicon16x16.jpg'), QSize(16, 16))
        my_icon.addFile(path.join('assets', 'favicon24x24.jpg'), QSize(24, 24))
        my_icon.addFile(path.join('assets', 'favicon32x32.jpg'), QSize(32, 32))
        my_icon.addFile(path.join('assets', 'favicon48x48.jpg'), QSize(48, 48))
        my_icon.addFile(path.join('assets', 'favicon64x64.jpg'), QSize(64, 64))
        my_icon.addFile(
            path.join('assets', 'favicon256x256.jpg'), QSize(256, 256))
        return my_icon

    def readStyleSheet(self) -> str:
        """liest das StyleSheet als String ein"""
        file_path = Path(os.path.abspath(__file__)
                         ).parent.joinpath('stylesheet.css')
        with closing(open(file_path)) as infile:
            styles = infile.read()
        return styles

    def __setDesign(self) -> None:
        """Setzt die StyleSheets usw"""
        self.setStyleSheet(self.readStyleSheet())

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
        super().show()
        screenSize = QScreen.availableGeometry(QApplication.primaryScreen())
        winXpos = ((screenSize.width() - self.width())/2)
        winYpos = ((screenSize.height() - self.height())/2)
        self.move(winXpos, winYpos)

    def processEvent(self, event: AppEvent):
        self.show()
