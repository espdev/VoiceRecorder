# -*- coding: utf-8 -*-

import os
import typing as t

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from PyQt5 import QtCore

from . import settings
from . import recordsmodel


class RecordsManager(QtCore.QObject):
    """Manages records
    """

    encode_progress = QtCore.pyqtSignal(int)

    def __init__(self, parent: t.Optional[QtCore.QObject] = None):
        super().__init__(parent)

        self._settings = settings.Settings(self)
        self._records_dir = self._settings.get_records_directory()

        self._records_db = TinyDB(self._settings.get_records_database_path(),
                                  storage=CachingMiddleware(JSONStorage))
        self._records_model = recordsmodel.RecordsTableModel(self._records_db, parent=self)
        self._records_sort_proxy_model = recordsmodel.RecordsSortProxyModel(self)
        self._records_sort_proxy_model.setSourceModel(self._records_model)

        self._remove_nonexistent_records()

    def __del__(self):
        self._records_db.close()

    @property
    def records_db(self) -> TinyDB:
        return self._records_db

    @property
    def records_model(self) -> recordsmodel.RecordsSortProxyModel:
        return self._records_sort_proxy_model

    def add_record(self, record):
        if not os.path.exists(self._records_dir):
            os.makedirs(self._records_dir)

        self._records_model.beginResetModel()

        self._records_db.insert({
            'filename': record.filename,
            'duration': record.duration,
            'timestamp': record.timestamp,
        })

        self._records_model.endResetModel()

    def remove_record(self, record_info: dict):
        fname = record_info['filename']

        if os.path.exists(fname):
            os.remove(fname)

        self._records_model.beginResetModel()
        self._records_db.remove(Query().filename == fname)
        self._records_model.endResetModel()

    def remove_records(self, records: t.List[dict]):
        fnames = [record['filename'] for record in records]

        for fname in fnames:
            if os.path.exists(fname):
                os.remove(fname)

        self._records_model.beginResetModel()
        self._records_db.remove(Query().filename.one_of(fnames))
        self._records_model.endResetModel()

    def _remove_nonexistent_records(self):
        fnames = []

        for record in self._records_db:
            filename = record['filename']

            if not os.path.exists(filename):
                fnames.append(filename)

        if fnames:
            self._records_model.beginResetModel()
            self._records_db.remove(Query().filename.one_of(fnames))
            self._records_model.endResetModel()
