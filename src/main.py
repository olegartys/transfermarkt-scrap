#!/usr/bin/env python3

import sys
import argparse

from PyQt5 import QtWidgets

from app_config import AppConfig
from ui.main_window import MainWindow


def main(args):
    app = QtWidgets.QApplication(sys.argv)

    app_config = AppConfig(args.config_path)

    window = MainWindow(app_config)
    window.show()

    return app.exec_()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('config_path', type=str, help='path to the configuration file')

    args = parser.parse_args()

    sys.exit(main(args))
