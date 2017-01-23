# -*- coding: utf-8 -*-

"""
"""

import os
import datetime

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from . import mainwindow_ui
from . import audiorecorder
from . import recordsmanager
from . import helperutils

from . import __app_name__
from . import __version__


class MainWindow(QtWidgets.QMainWindow):

    RECORD_DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.__ui = mainwindow_ui.Ui_MainWindow()
        self.__ui.setupUi(self)

        self.setWindowTitle(f'{__app_name__} - {__version__}')
        self.ui.labelRecordDuration.setVisible(False)

        self.ui.tableRecords.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        self.ui.tableRecords.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.ui.tableRecords.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)

        settings_fname = os.path.normpath(
            os.path.join(helperutils.get_app_config_dir(), __app_name__+'.ini'))

        self.__settings = QtCore.QSettings(
            settings_fname, QtCore.QSettings.IniFormat, self)
        self.__settings_group = helperutils.qsettings_group(self.__settings)

        self.__audio_recorder = audiorecorder.AudioRecorder(parent=self)
        self.__records_manager = recordsmanager.RecordsManager(parent=self)

        self.ui.pbRecordingStartAndStop.toggled.connect(self.__on_start_stop)
        self.ui.pbRecordingPause.toggled.connect(self.__on_pause)
        self.ui.pbRemoveRecords.clicked.connect(self.__remove_selected_records)

        self.ui.tableRecords.cellDoubleClicked.connect(self.__on_play_record)
        self.ui.tableRecords.itemSelectionChanged.connect(
            self.__on_change_selected_records)
        self.ui.tableRecords.installEventFilter(self)

        self.__audio_recorder.record_updated.connect(
            self.__on_update_duration_time)

        self.__read_settings()
        self.__update_records_info()

    def closeEvent(self, event):
        self.__write_settings()

    def eventFilter(self, obj, event: QtGui.QKeyEvent):
        if obj is not self.ui.tableRecords:
            return False
        if event.type() != QtCore.QEvent.KeyPress:
            return False
        if event.key() != QtCore.Qt.Key_Delete:
            return False

        self.__remove_selected_records()
        return True

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

    def __on_play_record(self, index):
        record_info = self.ui.tableRecords.item(index, 0).data(
            QtCore.Qt.UserRole)

        record_url = QtCore.QUrl(record_info.filename.replace('\\', '/'))
        QtGui.QDesktopServices.openUrl(record_url)

    def __on_change_selected_records(self):
        is_selected = len(self.ui.tableRecords.selectedItems()) > 0
        self.ui.pbRemoveRecords.setEnabled(is_selected)

    def __start_recording(self):
        self.__audio_recorder.record()

    def __pause_recording(self):
        self.__audio_recorder.stop()

    def __stop_recording(self):
        self.__audio_recorder.stop()
        self.__save_record()
        self.__audio_recorder.clear()
        self.__on_update_duration_time()

    def __save_record(self):
        record_info = self.__records_manager.save_record(
            self.__audio_recorder.get_record())

        self.__add_record_info_to_table(0, record_info)

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

    def __add_record_info_to_table(self, index, record_info):
        self.ui.tableRecords.insertRow(index)

        date_item = QtWidgets.QTableWidgetItem(
            record_info.date.strftime(self.RECORD_DATETIME_FORMAT))
        date_item.setData(QtCore.Qt.UserRole, record_info)

        dur_item = QtWidgets.QTableWidgetItem(str(record_info.duration))
        dur_item.setTextAlignment(QtCore.Qt.AlignCenter)

        self.ui.tableRecords.setItem(index, 0, date_item)
        self.ui.tableRecords.setItem(index, 1, dur_item)

    def __update_records_info(self):
        records_info = self.__records_manager.get_records_info()
        self.ui.tableRecords.clearContents()
        self.ui.tableRecords.setRowCount(0)

        for i, record_info in enumerate(records_info):
            self.__add_record_info_to_table(i, record_info)

    def __remove_selected_records(self):
        selected_items = self.ui.tableRecords.selectedItems()

        if not selected_items:
            return False

        records_for_remove = [
            (item, item.data(QtCore.Qt.UserRole))
            for item in selected_items if item.data(QtCore.Qt.UserRole)
        ]

        for item, record_info in records_for_remove:
            row = self.ui.tableRecords.row(item)
            self.__records_manager.remove_record(record_info)
            self.ui.tableRecords.removeRow(row)
