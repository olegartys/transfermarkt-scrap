from PyQt5.QtWidgets import QHeaderView, QMainWindow, QErrorMessage, QMessageBox
from PyQt5.QtCore import Qt

from pyqtspinner.spinner import WaitingSpinner

from ui.main_window_ui import Ui_MainWindow
from ui.export_dialog import ExportDialogWindow

from model.players_manager import PlayersManager
from model.players_table_model import PlayersTableModel

from misc.csv_exporter import CsvExporter
from misc.xlsx_exporter import XlsxExporter


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app_config):
        super(self.__class__, self).__init__()

        self.setupUi(self)

        self.app_config = app_config

        self.spinner = WaitingSpinner(self.playersTable, True, True, Qt.ApplicationModal)

        # setup table header so it stretches to all the width
        self.playersTable.horizontalHeader().setStretchLastSection(True)
        self.playersTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # setup table model
        self.players_manager = PlayersManager(app_config)

        self.players_table_model = PlayersTableModel(app_config, self.players_manager, parent=self)
        self.playersTable.setModel(self.players_table_model)

        # Connect signal handlers
        self.exitButton.clicked.connect(self.close)
        self.refreshButton.clicked.connect(self.refresh)
        self.exportButton.clicked.connect(self.export_table_data)

    def set_table_inactive(self):
        self.spinner.start()

    def set_table_active(self):
        self.spinner.stop()

    def refresh(self):
        self.players_table_model.drop_data()
        self.playersTable.scrollToTop()

    def export_table_data(self):
        self.set_table_inactive()

        export_format, output_filename = ExportDialogWindow(self.app_config).get_export_params()

        exporter = None

        if export_format == 'csv':
            exporter = CsvExporter()

        elif export_format == 'xlsx':
            exporter = XlsxExporter()

        else:
            self.set_table_active()
            QErrorMessage(self).showMessage('Неизвестный формат экспорта {}'.format(export_format))
            return

        exporter.export(self.players_manager, output_filename)

        self.draw_msg('Данные экспортированы в файл {}'.format(output_filename))

        self.set_table_active()

    def draw_msg(self, text):
        msg = QMessageBox(self)
        msg.setText(text)
        msg.exec()
