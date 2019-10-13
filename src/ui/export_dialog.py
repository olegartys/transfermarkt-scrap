import os

from PyQt5.QtWidgets import QDialog, QFileDialog

from ui.export_dialog_ui import Ui_Dialog


class ExportDialogWindow(QDialog, Ui_Dialog):
    ''' Dialog window used to export data from the table. '''

    def __init__(self, app_config):
        ''' Constructs new ExportDialogWindow istance.

        Parameters
        ----------
            app_config : AppConfig
                Instance of application configuration file.

        '''

        super(self.__class__, self).__init__()

        config = app_config.export_dialog
        self.default_base_filename = config['defaultFileName']

        self.setupUi(self)

        for f in config['formats']:
            self.formatCombo.addItem(f)

        self.formatCombo.currentIndexChanged.connect(self._on_format_changed)

        self.outputFileEdit.setText(self._default_filename())

        self.outputFileButton.clicked.connect(self._browse)

        self.buttonBox.accepted.connect(self._on_accept)
        self.buttonBox.rejected.connect(self._on_reject)

        self.current_format = self.formatCombo.currentText()
        self.output_file_name = self.outputFileEdit.text()

    def _browse(self):
        ''' Callback to draw QFileDialog widget '''

        self.output_file_name = QFileDialog.getOpenFileName(self)[0]

        if len(self.output_file_name) != 0:
            self.outputFileEdit.setText(self.output_file_name)

    def _on_accept(self):
        ''' Callback called when 'ok' clicked.
        Reads the current format and filename values.
        '''

        self.current_format = self.formatCombo.currentText()
        self.output_file_name = self.outputFileEdit.text()

        self.close()

    def _on_reject(self):
        ''' Callback called when 'cancel' clicked.
        Clears format and filename values.
        '''

        self.current_format = ''
        self.output_file_name = ''

        self.close()

    def _on_format_changed(self):
        ''' Callback called when format changed.
        Changes the default filename according to the format extension.
        '''

        self.outputFileEdit.setText(self._default_filename())

    def _default_filename(self):
        ''' Return the default filename string for current format chosen. '''

        return os.path.join(os.getcwd(), self.default_base_filename + '.' + self.formatCombo.currentText())

    def get_export_params(self):
        ''' Draws dialog and returns choosen format and file name to caller. '''

        self.exec()

        return (self.current_format, self.output_file_name)
