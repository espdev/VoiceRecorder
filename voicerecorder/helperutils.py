# -*- coding: utf-8 -*-

"""
"""

import sys
import datetime
import typing as t

from PyQt5 import QtCore


AV_TIME_BASE = 1000000


def format_duration(duration: int):
    duration_delta = datetime.timedelta(milliseconds=duration)

    mm, ss = divmod(duration_delta.seconds, 60)
    hh, mm = divmod(mm, 60)

    s = "%d:%02d:%02d" % (hh, mm, ss)

    return s


def format_timestamp(timestamp: t.Union[int, float], fmt: str):
    return datetime.datetime.fromtimestamp(timestamp).strftime(f'{fmt}')


def set_exception_hook():
    def _exception_hook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)

    sys.excepthook = _exception_hook


def get_app_config_dir():
    return QtCore.QStandardPaths.standardLocations(
        QtCore.QStandardPaths.AppConfigLocation)[0]


def get_documents_dir():
    return QtCore.QStandardPaths.standardLocations(
        QtCore.QStandardPaths.DocumentsLocation)[0]
