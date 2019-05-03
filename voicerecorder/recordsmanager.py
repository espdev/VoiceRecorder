# -*- coding: utf-8 -*-

"""
"""

import os
import datetime
import time
import wave

import av

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from PyQt5 import QtCore

from . import __app_name__
from . import helperutils
from . import recordsmodel


RECORDS_DATABASE_NAME = 'records_db.json'
RECORD_DATETIME_FORMAT = '%d-%m-%Y-%H-%M-%S'
RECORD_ENCODE_FORMAT = ('libvorbis', '.ogg')


class RecordsManager(QtCore.QObject):
    """Manages records
    """

    encode_progress = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._default_records_dir = self._get_default_records_dir()
        self._records_dir = self._default_records_dir

        self._records_db = TinyDB(self._get_records_db_path(),
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

    def add_record(self, record_info: dict):
        if not os.path.exists(self._records_dir):
            os.makedirs(self._records_dir)
        self._records_model.beginResetModel()
        self._add_record(record_info)
        self._records_model.endResetModel()

    def remove_record(self, record_info: dict):
        fname = record_info['filename']
        fname_ext = helperutils.get_filename_with_extension(fname)

        if os.path.exists(fname_ext):
            os.remove(fname_ext)

        self._records_model.beginResetModel()
        query = Query()
        self._records_db.remove(query.filename == fname)
        self._records_model.endResetModel()

    def read_settings(self, settings: QtCore.QSettings):
        with helperutils.qsettings_group(settings)('Path'):
            self._records_dir = settings.value(
                'RecordsDirectory', self._default_records_dir)

    def write_settings(self, settings: QtCore.QSettings):
        with helperutils.qsettings_group(settings)('Path'):
            if not settings.contains('RecordsDirectory'):
                settings.setValue('RecordsDirectory', self._records_dir)

    def _remove_nonexistent_records(self):
        removed = []

        for record in self._records_db:
            filename = record['filename']
            filename_ext = helperutils.get_filename_with_extension(filename)

            if not os.path.exists(filename_ext):
                removed.append(filename)

        if removed:
            self._records_model.beginResetModel()
            query = Query()
            self._records_db.remove(query.filename.one_of(removed))
            self._records_model.endResetModel()

    def _add_record(self, record_info):
        record_timestamp = int(time.time())
        record_date_str = helperutils.format_timestamp(record_timestamp, RECORD_DATETIME_FORMAT)

        record_file_name = f'voice-{record_date_str}'
        record_file_path = os.path.join(self._records_dir, record_file_name)

        self._encode(record_info['filename'], record_file_path)
        os.remove(record_info['filename'])

        record = {
            'filename': record_file_path,
            'duration': record_info['duration'],
            'timestamp': record_timestamp,
        }

        self._records_db.insert(record)

    def _encode(self, wavfname, outfname, fmt=RECORD_ENCODE_FORMAT):
        inp = av.open(wavfname, 'r')
        out = av.open(outfname + fmt[1], 'w')

        ostream = out.add_stream(fmt[0])

        with wave.open(wavfname, 'rb') as wav:
            num_frames = wav.getnframes()
        num_encoded_frames = 0

        for frame in inp.decode(audio=0):
            frame.pts = None

            for p in ostream.encode(frame):
                out.mux(p)

            num_encoded_frames += frame.samples
            self.encode_progress.emit(int(100 * num_encoded_frames / num_frames))

        for p in ostream.encode(None):
            out.mux(p)

        out.close()

    @staticmethod
    def _get_default_records_dir():
        return os.path.normpath(
            os.path.join(helperutils.get_documents_dir(), __app_name__))

    @staticmethod
    def _get_records_db_path():
        return os.path.normpath(
            os.path.join(helperutils.get_app_config_dir(), RECORDS_DATABASE_NAME))
