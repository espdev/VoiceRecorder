from dataclasses import dataclass
import os

from PySide6.QtCore import QObject, QModelIndex
from PySide6.QtCore import Qt
from tinydb import Query, TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

from .recordsmodel import RecordsTableModel, RecordsSortProxyModel
from .settings import Settings


@dataclass
class Record:
    filename: str
    duration: int
    timestamp: int


class RecordsManager(QObject):
    """Manages records"""

    def __init__(self, settings: Settings, parent: QObject | None = None):
        super().__init__(parent)

        self._settings = settings
        self._records_dir = self._settings.get_records_directory()

        self._records_db = TinyDB(
            self._settings.get_records_database_path(), storage=CachingMiddleware(JSONStorage), create_dirs=True
        )

        self._records_model = RecordsTableModel(parent=self)
        self._records_model.set_records(self._records_db.all())

        self._records_sort_proxy_model = RecordsSortProxyModel(self)
        self._records_sort_proxy_model.setSourceModel(self._records_model)

        self._remove_nonexistent_records()

    def __del__(self):
        self.close()

    @property
    def records_db(self) -> TinyDB:
        return self._records_db

    @property
    def records_model(self) -> RecordsSortProxyModel:
        return self._records_sort_proxy_model

    def add_record(self, record: Record):
        if not os.path.exists(self._records_dir):
            os.makedirs(self._records_dir)

        self._records_db.insert(
            {
                'filename': record.filename,
                'duration': record.duration,
                'timestamp': record.timestamp,
            }
        )
        self._records_model.set_records(self._records_db.all())

    def remove_record(self, record_info: dict):
        fname = record_info['filename']

        if os.path.exists(fname):
            os.remove(fname)

        self._records_db.remove(Query().filename == fname)
        self._records_model.set_records(self._records_db.all())

    def remove_records(self, indexes: list[QModelIndex]):
        records = [index.data(Qt.ItemDataRole.UserRole) for index in indexes]
        fnames = [record['filename'] for record in records]

        for fname in fnames:
            if os.path.exists(fname):
                os.remove(fname)

        self._records_db.remove(Query().filename.one_of(fnames))
        self._records_model.set_records(self._records_db.all())

    def close(self):
        self._records_db.close()

    def _remove_nonexistent_records(self):
        fnames = []

        for record in self._records_db:
            filename = record['filename']

            if not os.path.exists(filename):
                fnames.append(filename)

        if fnames:
            self._records_db.remove(Query().filename.one_of(fnames))
            self._records_model.set_records(self._records_db.all())
