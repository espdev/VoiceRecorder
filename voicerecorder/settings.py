# -*- coding: utf-8 -*-

import os
import contextlib
import typing as t

from PyQt5 import QtCore

from . import __app_name__


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
    """Stores and manages the application settings
    """

    def __init__(self, parent: QtCore.QObject = None):
        self._filename = os.path.normpath(
            os.path.join(self.get_app_config_dir(), __app_name__ + '.ini'))

        self._settings = QtCore.QSettings(self._filename, QtCore.QSettings.IniFormat, parent)
        self._settings_group = _qsettings_group_factory(self._settings)

    @property
    def filename(self):
        return self._filename

    @property
    def s(self) -> QtCore.QSettings:
        return self._settings

    @property
    def group(self):
        return self._settings_group

    @staticmethod
    def get_app_config_dir():
        return QtCore.QStandardPaths.standardLocations(
            QtCore.QStandardPaths.AppConfigLocation)[0]

    def set_default(self, group: str, key: str, value: t.Any):
        with self.group(group) as s:
            if s.contains(key):
                value = s.value(key)
            else:
                s.setValue(key, value)
        return value

    def get_records_directory(self):
        documents_dir = QtCore.QStandardPaths.standardLocations(
            QtCore.QStandardPaths.DocumentsLocation)[0]
        default_records_dir = os.path.normpath(os.path.join(documents_dir, __app_name__))
        return os.path.normpath(self.set_default('Record', 'RecordsDirectory', default_records_dir))

    def get_temporary_records_directory(self):
        records_dir = self.get_records_directory()
        return os.path.normpath(self.set_default('Record', 'TemporaryRecordsDirectory', records_dir))

    def get_audio_format(self):
        default_audio_format = 'libvorbis/.ogg'
        fmt = self.set_default('Audio', 'Format', default_audio_format)
        codec, ext = fmt.split('/')

        return codec, ext

    def get_records_database_path(self):
        default_path = os.path.normpath(
            os.path.join(self.get_app_config_dir(), 'records_db.json'))
        return os.path.normpath(self.set_default('Record', 'RecordsDatabasePath', default_path))

    def get_record_filename_datetime_format(self):
        default_format = '%d-%m-%Y-%H-%M-%S'
        return self.set_default('Record', 'RecordFilenameDatetimeFormat', default_format)

    def get_record_table_datetime_format(self):
        default_format = '%d.%m.%Y %H:%M:%S'
        return self.set_default('Record', 'RecordTableDatetimeFormat', default_format)
