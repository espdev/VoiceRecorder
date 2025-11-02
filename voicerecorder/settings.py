from typing import Any, ContextManager
from contextlib import contextmanager
from pathlib import Path

from PySide6.QtCore import QByteArray, QObject, QSettings, QStandardPaths
from PySide6.QtMultimedia import QMediaDevices, QMediaFormat
from PySide6.QtWidgets import QMainWindow

from .constants import APP_NAME


class Settings:
    """Stores and manages the application settings"""

    def __init__(self, parent: QObject | None = None):
        self._settings = QSettings(str(self.settings_file_path()), QSettings.Format.IniFormat, parent)

    @staticmethod
    def app_config_dir() -> Path:
        return Path(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppConfigLocation)[0])

    def settings_file_path(self) -> Path:
        return self.app_config_dir() / f'{APP_NAME}.ini'

    def records_db_path(self) -> Path:
        return self.app_config_dir() / 'records.db'

    @contextmanager
    def group(self, name: str) -> ContextManager[QSettings]:  # noqa
        self._settings.beginGroup(name)
        try:
            yield self._settings  # noqa
        finally:
            self._settings.endGroup()

    def set_default(self, group: str, key: str, value: Any) -> Any:
        with self.group(group) as s:
            if s.contains(key):
                value = s.value(key)
            else:
                s.setValue(key, value)
        return value

    def records_directory(self) -> Path:
        documents_dir = Path(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DocumentsLocation)[0])
        default_records_dir = documents_dir / APP_NAME
        return Path(self.set_default('Record', 'RecordsDirectory', default_records_dir.as_posix()))

    def record_filename_format(self) -> str:
        default_format = 'record-%d-%m-%Y-%H-%M-%S'
        return self.set_default('Record', 'RecordFilenameFormat', default_format)

    def record_table_format(self) -> str:
        default_format = '%d.%m.%Y %H:%M:%S'
        return self.set_default('Record', 'RecordTableFormat', default_format)

    def restory_window_state(self, window: QMainWindow) -> None:
        geometry = self.set_default('UI', 'WindowGeometry', window.saveGeometry())
        state = self.set_default('UI', 'WindowState', window.saveState())

        window.restoreGeometry(geometry)
        window.restoreState(state)

    def set_window_state(self, window: QMainWindow) -> None:
        with self.group('UI') as s:
            s.setValue('WindowGeometry', window.saveGeometry())
            s.setValue('WindowState', window.saveState())

    def get_audio_input_id(self) -> QByteArray:
        default_input_id = QMediaDevices.defaultAudioInput().id
        return self.set_default('Audio', 'Input', default_input_id)

    def set_audio_input_id(self, audio_input_id: QByteArray) -> None:
        with self.group('Audio') as s:
            s.setValue('Input', audio_input_id)

    def get_audio_codec(self) -> QMediaFormat.AudioCodec:
        default_codec = QMediaFormat.AudioCodec.Opus
        codec = self.set_default('Record', 'AudioCodec', hex(default_codec.value))
        return QMediaFormat.AudioCodec(int(codec, 16))

    def set_audio_codec(self, codec: QMediaFormat.AudioCodec) -> None:
        with self.group('Record') as s:
            s.setValue('AudioCodec', hex(codec.value))

    def get_file_format(self) -> QMediaFormat.FileFormat:
        default_format = QMediaFormat.FileFormat.Matroska
        file_format = self.set_default('Record', 'FileFormat', hex(default_format.value))
        return QMediaFormat.FileFormat(int(file_format, 16))

    def set_file_format(self, file_format: QMediaFormat.FileFormat) -> None:
        with self.group('Record') as s:
            s.setValue('FileFormat', hex(file_format.value))
