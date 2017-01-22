# -*- coding: utf-8 -*-

"""
"""

import contextlib

from PyQt5 import QtCore


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
