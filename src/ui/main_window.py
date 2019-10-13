from PyQt5.QtWidgets import QHeaderView, QMainWindow, QErrorMessage, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

from pyqtspinner.spinner import WaitingSpinner

from ui.main_window_ui import Ui_MainWindow
from ui.export_dialog import ExportDialogWindow

from model.players_manager import PlayersManager
from model.players_table_model import PlayersTableModel

from misc.csv_exporter import CsvExporter
from misc.xlsx_exporter import XlsxExporter


class MainWindow(QMainWindow, Ui_MainWindow):
    ''' The main application window. '''

    def __init__(self, app_config):
        ''' Constructs new MainWindow istance.

        Parameters
        ----------
            app_config : AppConfig
                Instance of application config.
        '''

        super(self.__class__, self).__init__()

        self.setupUi(self)

        self.app_config = app_config

        self.setWindowTitle(self.app_config.general['appName'])

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

        self.aboutAction.triggered.connect(self.show_about_dialog)

        self.gotoRowOk.clicked.connect(self.scroll_to_row)

        self.gotoRow.setValidator(QIntValidator(1, self.app_config.players_table_model['maxRowCount']))

    def set_table_inactive(self):
        ''' Set the table view state to inactive. '''

        self.spinner.start()

    def set_table_active(self):
        ''' Set the table view state to active. '''

        self.spinner.stop()

    def refresh(self):
        ''' Callback called on 'refresh' button clicked.
        Drops the model internal cache and scroll to the top of the table.
        '''

        self.players_table_model.drop_data()
        self.playersTable.scrollToTop()

    def export_table_data(self):
        ''' Callback called on 'export' button clicked.
        Draw export dialog window, read params and dump the data on disk
        using the particular exporter.
        '''

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

        self.show_msg('Данные экспортированы в файл {}'.format(output_filename))

        self.set_table_active()

    def scroll_to_row(self):
        ''' Callback called to scroll the table view to a particular row. '''

        row = int(self.gotoRow.text())

        self.players_table_model.goto_row(row)

        # FIXME: only after the second scroll it actually happens
        self.playersTable.scrollTo(self.players_table_model.index(row, 0))
        self.playersTable.scrollTo(self.players_table_model.index(row, 0))

    def show_about_dialog(self):
        ''' Callback called to draw 'about' dialog. '''

        general_config = self.app_config.general

        msg = '''
        {} (appVersion={})

        Разработана студентами группы МКС-183:

        {}
        {}
        '''.format(general_config['appName'], general_config['appVersion'],
            general_config['developerList'][0], general_config['developerList'][1])

        self.show_msg(msg)

    def show_msg(self, text):
        ''' Helper method to show Qt message box. '''

        msg = QMessageBox(self)
        msg.setText(text)
        msg.exec()
