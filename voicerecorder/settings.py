# -*- coding: utf-8 -*-

import os
import contextlib

from PyQt5 import QtCore

from . import __app_name__
from . import helperutils


def _qsettings_group_factory(settings: QtCore.QSettings):
    @contextlib.contextmanager
    def qsettings_group_context(group_name: str):
        settings.beginGroup(group_name)
        yield settings
        settings.endGroup()

    return qsettings_group_context


class SettingsMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SettingsMeta, cls).__call__(*args, **kwargs)
        return cls._instance


class Settings(metaclass=SettingsMeta):
    """Stores application settings
    """

    def __init__(self, parent: QtCore.QObject = None):
        self._filename = os.path.normpath(
            os.path.join(helperutils.get_app_config_dir(), __app_name__ + '.ini'))

        self._settings = QtCore.QSettings(self._filename, QtCore.QSettings.IniFormat, parent)
        self._settings_group = _qsettings_group_factory(self._settings)

    @property
    def filename(self):
        return self._filename

    @property
    def group(self):
        return self._settings_group
