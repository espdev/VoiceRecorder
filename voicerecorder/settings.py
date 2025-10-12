from typing import Any, ContextManager
from contextlib import contextmanager
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, QStandardPaths
from PySide6.QtMultimedia import QMediaFormat

from .constants import APP_NAME


class Settings:
    """Stores and manages the application settings"""

    def __init__(self, parent: QObject | None = None):
        self._file_path = self.get_app_config_dir() / f'{APP_NAME}.ini'
        self._settings = QSettings(str(self._file_path), QSettings.Format.IniFormat, parent)

    @contextmanager
    def group(self, name: str) -> ContextManager[QSettings]:
        self._settings.beginGroup(name)
        try:
            yield self._settings
        finally:
            self._settings.endGroup()

    @property
    def file_path(self) -> Path:
        return self._file_path

    @staticmethod
    def get_app_config_dir() -> Path:
        return Path(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppConfigLocation)[0])

    def set_default(self, group: str, key: str, value: Any) -> Any:
        with self.group(group) as s:
            if s.contains(key):
                value = s.value(key)
            else:
                s.setValue(key, value)
        return value

    def get_records_directory(self) -> Path:
        documents_dir = Path(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DocumentsLocation)[0])
        default_records_dir = documents_dir / APP_NAME
        return Path(self.set_default('Record', 'RecordsDirectory', default_records_dir.as_posix()))

    def get_records_database_path(self) -> Path:
        default_path = self.get_app_config_dir() / 'records_db.json'
        return Path(self.set_default('Record', 'RecordsDatabasePath', default_path.as_posix()))

    def get_record_filename_format(self) -> str:
        default_format = 'record-%d-%m-%Y-%H-%M-%S'
        return self.set_default('Record', 'RecordFilenameFormat', default_format)

    def get_record_table_format(self) -> str:
        default_format = '%d.%m.%Y %H:%M:%S'
        return self.set_default('Record', 'RecordTableFormat', default_format)

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
