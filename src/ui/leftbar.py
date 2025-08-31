from PySide6.QtWidgets import QPushButton, QVBoxLayout, QFrame

from application.event_dispatcher import AppEvent, EventDispatcher


class LeftBar(QFrame):
    def __init__(self, parent, event_dispatcher: EventDispatcher):
        super().__init__(parent, lineWidth=1)
        self.event_dispatcher = event_dispatcher
        self._buildUi()

    def _buildUi(self):

        self.setLayout(QVBoxLayout())
        self.innerFrame = QFrame(self)
        self.layout().addWidget(self.innerFrame)

        self.btn_config = QPushButton("Datenbank konfigurieren")
        self.btn_config.clicked.connect(
            lambda evt: self.event_dispatcher.send(AppEvent(evt_type='start-config-db')))
        self.btn_editsuppliers = QPushButton('Lieferanten pflegen')
        self.btn_editsuppliers.clicked.connect(
            lambda evt: self.event_dispatcher.send(AppEvent(evt_type='edit-suppliers')))
        self.btn_invoices = QPushButton("Rechnungen importieren")
        self.btn_invoices.clicked.connect(lambda evt: self.event_dispatcher.send(
            AppEvent(evt_type='import-invoice', evt_data='edeka')))
        self.btn_paxan_orderconfirm = QPushButton("paxan-Bestell-\neingangsbestätigung\nimportieren")
        self.btn_paxan_orderconfirm.clicked.connect(
            lambda evt: self.event_dispatcher.send(
                AppEvent(
                    evt_type='import-paxan-orderconfirmation'
                )
            )
        )        
        self.btn_edeka_orderconfirm = QPushButton("EDEKA-Bestell-\neingangsbestätigung\nimportieren")
        #self.btn_edeka_orderconfirm.setEnabled(False)
        self.btn_edeka_orderconfirm.clicked.connect(
            lambda evt: self.event_dispatcher.send(
                AppEvent(
                    evt_type='import-edeka-orderconfirmation'
                )
            )
        )
        self.btn_article_input = QPushButton("Manuelle Artikelerfassung")
        self.btn_map_gtin = QPushButton("GTIN/EAN nachpflegen")
        self.btn_export_articles = QPushButton("Artikel exportieren")
        self.innerFrame.setLayout(QVBoxLayout())
        self.innerFrame.layout().addWidget(self.btn_config)
        self.innerFrame.layout().addWidget(self.btn_editsuppliers)
        self.innerFrame.layout().addWidget(self.btn_invoices)
        self.innerFrame.layout().addWidget(self.btn_paxan_orderconfirm)
        self.innerFrame.layout().addWidget(self.btn_edeka_orderconfirm)
        self.innerFrame.layout().addWidget(self.btn_article_input)
        self.innerFrame.layout().addWidget(self.btn_map_gtin)
        self.innerFrame.layout().addWidget(self.btn_export_articles)
        self.innerFrame.layout().addStretch(1)
