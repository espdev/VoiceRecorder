# -*- coding: utf-8 -*-

"""
"""

import os
import datetime
import time
import wave

import av
import tinydb
from PyQt5 import QtCore

from . import helperutils
from . import __app_name__


RECORDS_DATABASE_NAME = 'records_db.json'
DATETIME_FORMAT = '%d-%m-%Y-%H-%M-%S'
ENCODE_FORMAT = ('libvorbis', '.ogg')


class RecordsManager(QtCore.QObject):
    """
    """

    encode_progress = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__default_records_dir = os.path.normpath(
            os.path.join(helperutils.get_documents_dir(), __app_name__))
        self.__records_dir = self.__default_records_dir

        self._records_db = tinydb.TinyDB(
            os.path.join(helperutils.get_app_config_dir(), RECORDS_DATABASE_NAME))

    def save_record(self, record_info: dict):
        if not os.path.exists(self.__records_dir):
            os.makedirs(self.__records_dir)

        return self.__write_record_info(record_info)

    def get_records_info(self):
        records = []
        removed = []

        for record in self._records_db:
            filename = record['filename']

            if os.path.exists(helperutils.get_filename_with_extension(filename)):
                records.append(record)
            else:
                removed.append(record['filename'])

        r = tinydb.Query()
        self._records_db.remove(r.filename.one_of(removed))

        records.sort(key=lambda x: x['timestamp'])
        records.reverse()

        return records

    def remove_record(self, record_info: dict):
        file_name = record_info['filename']
        fname = helperutils.get_filename_with_extension(file_name)
        if os.path.exists(fname):
            os.remove(fname)

        r = tinydb.Query()
        self._records_db.remove(r.filename == file_name)

    def read_settings(self, settings: QtCore.QSettings):
        with helperutils.qsettings_group(settings)('Path'):
            self.__records_dir = settings.value(
                'RecordsDirectory', self.__default_records_dir)

    def write_settings(self, settings: QtCore.QSettings):
        with helperutils.qsettings_group(settings)('Path'):
            if not settings.contains('RecordsDirectory'):
                settings.setValue('RecordsDirectory', self.__records_dir)

    def __write_record_info(self, record_info):
        record_timestamp = int(time.time())
        record_date = datetime.datetime.fromtimestamp(record_timestamp)
        record_date_str = record_date.strftime(f'{DATETIME_FORMAT}')

        record_file_name = f'voice-{record_date_str}'
        record_file_path = os.path.join(self.__records_dir, record_file_name)

        self.__encode(record_info['filename'], record_file_path)
        os.remove(record_info['filename'])

        record = {
            'filename': record_file_path,
            'duration': record_info['duration'],
            'timestamp': record_timestamp,
        }

        self._records_db.insert(record)

        return record

    def __encode(self, wavfname, outfname, fmt=ENCODE_FORMAT):
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
