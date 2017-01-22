# -*- coding: utf-8 -*-

"""
"""

import os
import datetime

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from . import __app_name__
from . import __version__

from . import mainwindow_ui
from . import audiorecorder
from . import recordsmanager
from . import helperutils


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.__ui = mainwindow_ui.Ui_MainWindow()
        self.__ui.setupUi(self)

        self.setWindowTitle(f'{__app_name__} - {__version__}')
        self.ui.labelRecordDuration.setVisible(False)

        settings_fname = os.path.normpath(
            os.path.join(helperutils.get_app_config_dir(), __app_name__ + '.ini'))

        self.__settings = QtCore.QSettings(
            settings_fname, QtCore.QSettings.IniFormat, self)
        self.__settings_group = helperutils.qsettings_group(self.__settings)

        self.__audio_recorder = audiorecorder.AudioRecorder(parent=self)
        self.__records_manager = recordsmanager.RecordsManager(parent=self)

        self.ui.pbRecordingStartAndStop.toggled.connect(self.__on_start_stop)
        self.ui.pbRecordingPause.toggled.connect(self.__on_pause)

        self.__audio_recorder.record_updated.connect(
            self.__on_update_duration_time)

        self.__read_settings()

    def closeEvent(self, event):
        self.__write_settings()

    @property
    def ui(self):
        return self.__ui

    def __on_start_stop(self, is_checked):
        pb_title_text = {
            True: self.tr('Stop'),
            False: self.tr('Record'),
        }

        self.ui.pbRecordingStartAndStop.setText(pb_title_text[is_checked])
        self.ui.labelRecordDuration.setVisible(is_checked)

        if is_checked:
            self.__start_recording()
        else:
            self.__stop_recording()

    def __on_pause(self, is_checked):
        if is_checked:
            self.__pause_recording()
        else:
            self.__start_recording()

    def __on_update_duration_time(self):
        duration_delta = datetime.timedelta(
            seconds=int(self.__audio_recorder.duration))
        self.ui.labelRecordDuration.setText(str(duration_delta))

    def __start_recording(self):
        self.__audio_recorder.record()

    def __pause_recording(self):
        self.__audio_recorder.stop()

    def __stop_recording(self):
        self.__audio_recorder.stop()
        self.__write_to_file()
        self.__audio_recorder.clear()
        self.__on_update_duration_time()

    def __write_to_file(self):
        self.__records_manager.save_record(self.__audio_recorder.get_record())

    def __read_settings(self):
        with self.__settings_group('UI'):
            self.restoreGeometry(self.__settings.value(
                'WindowGeometry', self.saveGeometry()))
            self.restoreState(self.__settings.value(
                'WindowState', self.saveState()))

        self.__records_manager.read_settings(self.__settings)

    def __write_settings(self):
        with self.__settings_group('UI'):
            self.__settings.setValue('WindowGeometry', self.saveGeometry())
            self.__settings.setValue('WindowState', self.saveState())

        self.__records_manager.write_settings(self.__settings)
