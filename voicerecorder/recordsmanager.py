# -*- coding: utf-8 -*-

"""
"""

import os
import datetime

import wave
import av

from PyQt5 import QtCore

from . import helperutils
from . import __app_name__


RECORDS_INFO_FILENAME = 'Records.ini'
DATETIME_FORMAT = '%d-%m-%Y-%H-%M-%S'
ENCODE_FORMAT = ('libvorbis', '.ogg')


class RecordsManager(QtCore.QObject):
    """
    """

    encode_progress = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        records_info_fname = os.path.join(
            helperutils.get_app_config_dir(), RECORDS_INFO_FILENAME)

        self.__records_info = QtCore.QSettings(
            records_info_fname, QtCore.QSettings.IniFormat, self)

        self.__default_records_dir = os.path.normpath(
            os.path.join(helperutils.get_documents_dir(), __app_name__))
        self.__records_dir = self.__default_records_dir

    def save_record(self, record_info: dict):
        if not os.path.exists(self.__records_dir):
            os.makedirs(self.__records_dir)

        return self.__write_record_info(record_info)

    def get_records_info(self):
        records_info = []
        settings_group = helperutils.qsettings_group(self.__records_info)

        for record in self.__records_info.childGroups():
            date = datetime.datetime.strptime(record, DATETIME_FORMAT)

            with settings_group(record):
                filename = self.__records_info.value('FileName')
                duration = self.__records_info.value('Duration', type=int)

            if os.path.exists(helperutils.get_filename_with_extension(filename)):
                records_info.append({
                    'filename': filename,
                    'date': date,
                    'duration': duration,
                })
            else:
                self.__records_info.remove(record)

        records_info.sort(key=lambda x: x['date'])
        records_info.reverse()

        return records_info

    def remove_record(self, record_info: dict):
        record_group = record_info['date'].strftime(DATETIME_FORMAT)

        fname = helperutils.get_filename_with_extension(record_info['filename'])
        if os.path.exists(fname):
            os.remove(fname)

        self.__records_info.remove(record_group)

    def read_settings(self, settings: QtCore.QSettings):
        with helperutils.qsettings_group(settings)('Path'):
            self.__records_dir = settings.value(
                'RecordsDirectory', self.__default_records_dir)

    def write_settings(self, settings: QtCore.QSettings):
        with helperutils.qsettings_group(settings)('Path'):
            if not settings.contains('RecordsDirectory'):
                settings.setValue('RecordsDirectory', self.__records_dir)

    def __write_record_info(self, record_info):
        record_date = datetime.datetime.now()
        record_date_str = record_date.strftime(f'{DATETIME_FORMAT}')

        record_file_name = f'voice-{record_date_str}'
        record_file_path = os.path.join(self.__records_dir, record_file_name)

        self.__encode(record_info['filename'], record_file_path)
        os.remove(record_info['filename'])

        with helperutils.qsettings_group(self.__records_info)(record_date_str):
            self.__records_info.setValue('FileName', record_file_path)
            self.__records_info.setValue('Duration', record_info['duration'])

        date = datetime.datetime.strptime(record_date_str, DATETIME_FORMAT)

        return {
            'filename': record_file_path,
            'date': date,
            'duration': record_info['duration'],
        }

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
