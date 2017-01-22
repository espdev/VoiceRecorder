# -*- coding: utf-8 -*-

"""
"""

import os
import datetime
import collections
import wave

from PyQt5 import QtCore

from . import helperutils
from . import audiorecorder
from . import __app_name__


RECORDS_INFO_FILENAME = 'Records.ini'
DATETIME_FORMAT = '%Y-%m-%d-%H-%M-%S'


SavedRecordInfo = collections.namedtuple(
    'SavedRecordInfo', ('filename', 'date', 'duration'))


class RecordsManager(QtCore.QObject):
    """
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        records_info_fname = os.path.join(
            helperutils.get_app_config_dir(), RECORDS_INFO_FILENAME)

        self.__records_info = QtCore.QSettings(
            records_info_fname, QtCore.QSettings.IniFormat, self)

        self.__default_records_dir = os.path.normpath(
            os.path.join(helperutils.get_documents_dir(), __app_name__))
        self.__records_dir = self.__default_records_dir

    def save_record(self, record: audiorecorder.AudioRecord):
        if not os.path.exists(self.__records_dir):
            os.makedirs(self.__records_dir)

        record_date = datetime.datetime.now()
        record_date_str = record_date.strftime(f'{DATETIME_FORMAT}')
        record_file_name = f'voice-{record_date_str}.wav'
        record_file_path = os.path.join(self.__records_dir, record_file_name)

        self.__write_record_info(record_file_path, record_date_str, record)

    def get_records_info(self):
        records_info = []
        settings_group = helperutils.qsettings_group(self.__records_info)

        for record in self.__records_info.childGroups():
            date = datetime.datetime.strptime(record, DATETIME_FORMAT)

            with settings_group(record):
                file_name = self.__records_info.value('FileName')
                duration = self.__records_info.value('Duration', type=float)

            if os.path.exists(file_name):
                records_info.append(SavedRecordInfo(
                    filename=file_name,
                    date=date,
                    duration=datetime.timedelta(seconds=int(duration)),
                ))
            else:
                self.__records_info.remove(record)

        return records_info

    def read_settings(self, settings: QtCore.QSettings):
        with helperutils.qsettings_group(settings)('Path'):
            self.__records_dir = settings.value(
                'RecordsDirectory', self.__default_records_dir)

    def write_settings(self, settings: QtCore.QSettings):
        with helperutils.qsettings_group(settings)('Path'):
            if not settings.contains('RecordsDirectory'):
                settings.setValue('RecordsDirectory', self.__records_dir)

    @staticmethod
    def __write_wav(filename, record):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(record.channels)
            wf.setsampwidth(record.sample_size)
            wf.setframerate(record.rate)
            wf.writeframes(record.data)

    def __write_record_info(self, filename, date_str, record):
        # TODO: use OGG/Vorbis audio format
        self.__write_wav(filename, record)

        with helperutils.qsettings_group(self.__records_info)(date_str):
            self.__records_info.setValue('FileName', filename)
            self.__records_info.setValue('Duration', record.duration)
