# -*- coding: utf-8 -*-

"""
VoiceRecorder is a simple application for voice recording

"""

import sys

from PyQt5 import QtWidgets

from voicerecorder import __app_name__
from voicerecorder import __version__

from voicerecorder import mainwindow


def set_exception_hook():
    def _exception_hook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
    sys.excepthook = _exception_hook


def main():
    set_exception_hook()

    app = QtWidgets.QApplication(sys.argv)

    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)

    win = mainwindow.MainWindow()
    win.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
