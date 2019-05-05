# -*- coding: utf-8 -*-

import os
import time
import shutil

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from PyQt5 import QtCore

from . import utils
from . import recordsmodel
from . import settings


class RecordsManager(QtCore.QObject):
    """Manages records
    """

    encode_progress = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._settings = settings.Settings(self)
        self._records_dir = self._settings.get_records_directory()

        self._records_db = TinyDB(self._settings.get_records_database_path(),
                                  storage=CachingMiddleware(JSONStorage))
        self._records_model = recordsmodel.RecordsTableModel(self._records_db, parent=self)

        self._remove_nonexistent_records()

    def __del__(self):
        self._records_db.close()

    @property
    def records_db(self) -> TinyDB:
        return self._records_db

    @property
    def records_model(self) -> QtCore.QAbstractTableModel:
        return self._records_model

    def add_record(self, record):
        if not os.path.exists(self._records_dir):
            os.makedirs(self._records_dir)

        self._records_model.beginResetModel()
        self._add_record(record)
        self._records_model.endResetModel()

    def remove_record(self, record_info: dict):
        fname = record_info['filename']

        if os.path.exists(fname):
            os.remove(fname)

        self._records_model.beginResetModel()
        query = Query()
        self._records_db.remove(query.filename == fname)
        self._records_model.endResetModel()

    def _remove_nonexistent_records(self):
        removed = []

        for record in self._records_db:
            filename = record['filename']

            if not os.path.exists(filename):
                removed.append(filename)

        if removed:
            self._records_model.beginResetModel()
            query = Query()
            self._records_db.remove(query.filename.one_of(removed))
            self._records_model.endResetModel()

    def _add_record(self, tmp_record):
        record_date_str = utils.format_timestamp(
            tmp_record.timestamp, self._settings.get_record_filename_datetime_format())

        _, ext = os.path.splitext(tmp_record.filename)
        record_file_name = f'record-{record_date_str}{ext}'
        record_file_path = os.path.join(self._records_dir, record_file_name)

        shutil.copy2(tmp_record.filename, record_file_path)

        record_info = {
            'filename': record_file_path,
            'duration': tmp_record.duration,
            'timestamp': tmp_record.timestamp,
        }

        self._records_db.insert(record_info)
