# -*- coding: utf-8 -*-

"""
"""

import sys
import contextlib
import datetime
import glob

from PyQt5 import QtCore


def format_duration(duration):
    duration_delta = datetime.timedelta(milliseconds=duration)

    mm, ss = divmod(duration_delta.seconds, 60)
    hh, mm = divmod(mm, 60)

    s = "%d:%02d:%02d" % (hh, mm, ss)

    return s


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


def qsettings_group(settings: QtCore.QSettings):
    """
    """
    @contextlib.contextmanager
    def qsettings_group_context(group_name: str):
        settings.beginGroup(group_name)
        yield
        settings.endGroup()
    return qsettings_group_context


def get_filename_with_extension(filename):
    f = glob.glob(filename + '.*')
    if f:
        return f[0]
    else:
        return ''
