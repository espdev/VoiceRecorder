"""
VoiceRecorder is a simple application for voice recording

"""

import os
import sys

from PySide6.QtWidgets import QApplication

from voicerecorder import mainwindow
from voicerecorder.constants import APP_NAME, APP_VERSION, PKG_NAME

os.environ['QT_ENABLE_EXPERIMENTAL_CODECS'] = '1'


# def set_exception_hook():
#     def _exception_hook(exctype, value, traceback):
#         sys.__excepthook__(exctype, value, traceback)
#
#     sys.excepthook = _exception_hook


def main():
    # set_exception_hook()

    app = QApplication(sys.argv)

    app.setApplicationName(PKG_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    win = mainwindow.MainWindow()
    win.show()

    return app.exec()
