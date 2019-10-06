import os

from PyQt5.QtWidgets import QDialog, QFileDialog

from ui.export_dialog_ui import Ui_Dialog


class ExportDialogWindow(QDialog, Ui_Dialog):
    def __init__(self, app_config):
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
        self.output_file_name = QFileDialog.getOpenFileName(self)[0]

        if len(self.output_file_name) != 0:
            self.outputFileEdit.setText(self.output_file_name)

    def _on_accept(self):
        self.current_format = self.formatCombo.currentText()
        self.output_file_name = self.outputFileEdit.text()
        self.close()

    def _on_reject(self):
        self.current_format = ''
        self.output_file_name = ''
        self.close()

    def _on_format_changed(self):
        self.outputFileEdit.setText(self._default_filename())

    def _default_filename(self):
        return os.path.join(os.getcwd(), self.default_base_filename + '.' + self.formatCombo.currentText())

    def get_export_params(self):
        self.exec()
        return (self.current_format, self.output_file_name)
