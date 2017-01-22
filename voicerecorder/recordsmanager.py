# -*- coding: utf-8 -*-

"""
"""

import os
import datetime
import collections
import wave
import typing

from PyQt5 import QtCore

from . import helperutils
from . import audiorecorder
from . import __app_name__


RECORDS_INFO_FILENAME = 'Records.ini'
DATETIME_FORMAT = '%Y-%m-%d-%H-%M-%S'


RecordInfo = collections.namedtuple(
    'RecordInfo', ('filename', 'date', 'duration'))
RecordInfoList = typing.List[RecordInfo]


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

        return self.__write_record_info(record)

    def get_records_info(self) -> RecordInfoList:
        records_info = []
        settings_group = helperutils.qsettings_group(self.__records_info)

        for record in self.__records_info.childGroups():
            date = datetime.datetime.strptime(record, DATETIME_FORMAT)

            with settings_group(record):
                filename = self.__records_info.value('FileName')
                duration = self.__records_info.value('Duration', type=float)

            if os.path.exists(filename):
                records_info.append(RecordInfo(
                    filename=filename,
                    date=date,
                    duration=datetime.timedelta(seconds=int(duration)),
                ))
            else:
                self.__records_info.remove(record)

        records_info.sort(key=lambda x: x.date)
        records_info.reverse()

        return records_info

    def remove_record(self, record_info: RecordInfo):
        record_group = record_info.date.strftime(DATETIME_FORMAT)

        os.remove(record_info.filename)
        self.__records_info.remove(record_group)

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

    def __write_record_info(self, record):
        record_date = datetime.datetime.now()
        record_date_str = record_date.strftime(f'{DATETIME_FORMAT}')

        record_file_name = f'voice-{record_date_str}.wav'
        record_file_path = os.path.join(self.__records_dir, record_file_name)

        # TODO: use OGG/Vorbis audio format
        self.__write_wav(record_file_path, record)

        with helperutils.qsettings_group(self.__records_info)(record_date_str):
            self.__records_info.setValue('FileName', record_file_path)
            self.__records_info.setValue('Duration', record.duration)

        date = datetime.datetime.strptime(record_date_str, DATETIME_FORMAT)
        duration = datetime.timedelta(seconds=int(record.duration))

        return RecordInfo(
            filename=record_file_path,
            date=date,
            duration=duration,
        )
