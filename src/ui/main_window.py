from PyQt5.QtWidgets import QHeaderView, QMainWindow
from PyQt5.QtCore import Qt

from pyqtspinner.spinner import WaitingSpinner

from ui.main_window_ui import Ui_MainWindow
from model.players_table_model import PlayersTableModel


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app_config):
        super(self.__class__, self).__init__()

        self.setupUi(self)

        self.spinner = WaitingSpinner(self.playersTable, True, True, Qt.ApplicationModal)

        self.exitButton.clicked.connect(self.close)

        # setup table header so it stretches to all the width
        self.playersTable.horizontalHeader().setStretchLastSection(True)
        self.playersTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.players_table_model = PlayersTableModel(app_config, parent=self)
        self.playersTable.setModel(self.players_table_model)

        self.refreshButton.clicked.connect(self.refresh)

    def set_table_inactive(self):
        self.spinner.start()

    def set_table_active(self):
        self.spinner.stop()

    def refresh(self):
        self.players_table_model.drop_data()
        self.playersTable.scrollToTop()
