# -*- coding: utf-8 -*-

"""
VoiceRecorder is a simple application for voice recording

"""

import sys
from PyQt5 import QtWidgets

from voicerecorder import __app_name__
from voicerecorder import __version__

from voicerecorder import mainwindow


def main():
    app = QtWidgets.QApplication(sys.argv)

    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)

    win = mainwindow.MainWindow()
    win.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
