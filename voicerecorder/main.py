"""
VoiceRecorder is a simple application for voice recording

"""

import sys

from PyQt5 import QtWidgets

from voicerecorder import mainwindow
from voicerecorder.constants import APP_NAME, APP_VERSION


def set_exception_hook():
    def _exception_hook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)

    sys.excepthook = _exception_hook


def main():
    set_exception_hook()

    app = QtWidgets.QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    win = mainwindow.MainWindow()
    win.show()

    return app.exec()
