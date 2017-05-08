# -*- coding: utf-8 -*-

"""
"""

import os
import functools
import itertools
import tempfile
import math

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtMultimedia

from . import mainwindow_ui
from . import mainwindow_rc

from . import audiolevel
from . import recordsmanager
from . import helperutils

from . import __app_name__
from . import __version__


class RecordingStatusBarInfo(QtWidgets.QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        status_icon = QtWidgets.QLabel()
        status_icon.setPixmap(QtGui.QPixmap(':icons/rec'))

        self._status_icon_opacity = QtWidgets.QGraphicsOpacityEffect(status_icon)
        self._status_icon_opacity.setOpacity(1.0)

        status_icon.setGraphicsEffect(self._status_icon_opacity)

        status_text = QtWidgets.QLabel()
        status_text.setText(self.tr('Recording...'))

        self._animation_timer = QtCore.QTimer(self)
        self._animation_timer.setInterval(50)
        self._animation_timer.timeout.connect(self._animate_record_icon)
        self._animation_timer.start()

        self._opacity_dec = 0.1

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(status_icon)
        layout.addWidget(status_text)
        layout.setContentsMargins(9, 0, 9, 0)

        self.setLayout(layout)

    def _animate_record_icon(self):
        opacity = round(
            self._status_icon_opacity.opacity() - self._opacity_dec, 2)

        if math.isclose(opacity, 0.0) or math.isclose(opacity, 1.0):
            self._opacity_dec = -self._opacity_dec

        self._status_icon_opacity.setOpacity(opacity)


class MainWindow(QtWidgets.QMainWindow):

    RECORD_DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.__ui = mainwindow_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.__level_monitors = [
            audiolevel.AudioLevelMonitor(),
            audiolevel.AudioLevelMonitor(),
        ]

        for levmon in self.__level_monitors:
            levmon.setVisible(False)
            levmon.setMinimumWidth(50)
            levmon.setMaximumWidth(250)
            levmon.setFrameStyle(QtWidgets.QFrame.StyledPanel)

            self.ui.layoutAudioLevels.addWidget(levmon)

        self.__recording_statusbar_info = RecordingStatusBarInfo()
        self.__recording_statusbar_info.setVisible(False)

        status_bar: QtWidgets.QStatusBar = self.statusBar()
        status_bar.addWidget(self.__recording_statusbar_info)

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

        self.__tmp_audio_fname = ''

        self.__audio_recorder = QtMultimedia.QAudioRecorder(self)

        self.__audio_levels_calculator = audiolevel.AudioLevelsCalculator(
            self, self.__audio_recorder)
        self.__audio_levels_calculator.levels_calculated.connect(
            self.__on_show_audio_levels)

        self.__records_manager = recordsmanager.RecordsManager(parent=self)

        self.ui.pbRecordingStartAndStop.toggled.connect(self.__on_start_stop)
        self.ui.pbRecordingPause.toggled.connect(self.__on_pause)
        self.ui.pbPlayRecords.clicked.connect(
            functools.partial(self.__on_play_record, None))
        self.ui.pbRemoveRecords.clicked.connect(self.__remove_selected_records)

        self.ui.tableRecords.cellDoubleClicked.connect(self.__on_play_record)
        self.ui.tableRecords.itemSelectionChanged.connect(
            self.__on_change_selected_records)
        self.ui.tableRecords.installEventFilter(self)

        self.__audio_recorder.durationChanged.connect(
            self.__on_update_duration_time)

        self.__collect_audioinputs()
        self.__setup_audiorecorder()
        self.__read_settings()
        self.__update_records_info()

    def closeEvent(self, event):
        self.__write_settings()

    def eventFilter(self, obj, event: QtGui.QKeyEvent):
        if obj is not self.ui.tableRecords:
            return False
        if event.type() != QtCore.QEvent.KeyPress:
            return False

        if event.key() == QtCore.Qt.Key_Delete:
            self.__remove_selected_records()
            return True

        return False

    @property
    def ui(self):
        return self.__ui

    def __on_show_audio_levels(self, levels: list):
        for mon, level in zip(self.__level_monitors, levels):
            mon.set_level(level)

    def __on_start_stop(self, is_checked):
        pb_title_text = {
            True: self.tr('Stop'),
            False: self.tr('Record'),
        }

        self.ui.pbRecordingStartAndStop.setText(pb_title_text[is_checked])
        self.ui.labelRecordDuration.setVisible(is_checked)
        self.ui.cmboxAudioInput.setEnabled(not is_checked)

        if is_checked:
            self.__start_recording()
        else:
            self.__stop_recording()

    def __on_pause(self, is_checked):
        if is_checked:
            self.__audio_recorder.pause()
        else:
            self.__audio_recorder.record()

    def __on_update_duration_time(self, duration):
        self.ui.labelRecordDuration.setText(
            helperutils.format_duration(duration))

    def __on_play_record(self, index=None):
        if index is None:
            indexes = self.ui.tableRecords.selectedIndexes()
            rows = self.__selected_rows(indexes)
            item = self.ui.tableRecords.item(rows[0][0].row(), 0)
        else:
            item = self.ui.tableRecords.item(index, 0)

        record_info = item.data(QtCore.Qt.UserRole)

        filename = helperutils.get_filename_with_extension(
            record_info['filename']).replace('\\', '/')

        record_url = QtCore.QUrl(filename)
        QtGui.QDesktopServices.openUrl(record_url)

    def __on_change_selected_records(self):
        selected_rows_count = len(self.__selected_rows(
            self.ui.tableRecords.selectedIndexes()))

        self.ui.pbRemoveRecords.setEnabled(selected_rows_count > 0)
        self.ui.pbPlayRecords.setEnabled(selected_rows_count == 1)

    def __start_recording(self):
        self.__tmp_audio_fname = tempfile.mktemp(
            dir=helperutils.get_app_config_dir(), suffix='.wav')

        self.__audio_recorder.setAudioInput(
            self.ui.cmboxAudioInput.currentData(QtCore.Qt.UserRole))
        self.__audio_recorder.setOutputLocation(
            QtCore.QUrl.fromLocalFile(self.__tmp_audio_fname))

        for levmon in self.__level_monitors:
            levmon.setVisible(True)

        self.__audio_recorder.record()

        self.__recording_statusbar_info.setVisible(True)
        self.ui.pbRecordingStartAndStop.setIcon(QtGui.QIcon(':icons/stop'))

    def __stop_recording(self):
        duration = self.__audio_recorder.duration()

        self.__audio_recorder.stop()
        self.__save_record({
            'filename': self.__tmp_audio_fname,
            'duration': duration,
        })

        self.__recording_statusbar_info.setVisible(False)
        self.__on_update_duration_time(0)

        for levmon in self.__level_monitors:
            levmon.setVisible(False)

        self.ui.pbRecordingStartAndStop.setIcon(QtGui.QIcon(':icons/record'))

    def __save_record(self, record_info):
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.WaitCursor))

        try:
            record_info = self.__records_manager.save_record(record_info)
        except Exception as err:
            QtWidgets.QMessageBox.critical(
                self, 'Unable to save record', f'{err}')
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        self.__add_record_info_to_table(0, record_info)

    def __collect_audioinputs(self):
        self.ui.cmboxAudioInput.addItem('Default', '')

        ainputs = self.__audio_recorder.audioInputs()
        for ainput in ainputs:
            self.ui.cmboxAudioInput.addItem(ainput, ainput)

    def __setup_audiorecorder(self):
        settings = QtMultimedia.QAudioEncoderSettings()

        settings.setCodec('')
        settings.setSampleRate(48000)
        settings.setBitRate(128000)
        settings.setChannelCount(2)
        settings.setQuality(QtMultimedia.QMultimedia.HighQuality)
        settings.setEncodingMode(
            QtMultimedia.QMultimedia.ConstantQualityEncoding)

        self.__audio_recorder.setEncodingSettings(
            settings, QtMultimedia.QVideoEncoderSettings(), '')

    def __read_settings(self):
        with self.__settings_group('UI'):
            self.restoreGeometry(self.__settings.value(
                'WindowGeometry', self.saveGeometry()))
            self.restoreState(self.__settings.value(
                'WindowState', self.saveState()))

        with self.__settings_group('Audio'):
            ainput = self.__settings.value('Input', 'Default')
            index = self.ui.cmboxAudioInput.findText(ainput)

            if index != -1:
                self.ui.cmboxAudioInput.setCurrentIndex(index)

        self.__records_manager.read_settings(self.__settings)

    def __write_settings(self):
        with self.__settings_group('UI'):
            self.__settings.setValue('WindowGeometry', self.saveGeometry())
            self.__settings.setValue('WindowState', self.saveState())

        with self.__settings_group('Audio'):
            self.__settings.setValue(
                'Input', self.ui.cmboxAudioInput.currentText())

        self.__records_manager.write_settings(self.__settings)

    def __add_record_info_to_table(self, index, record_info):
        self.ui.tableRecords.insertRow(index)

        date_item = QtWidgets.QTableWidgetItem(
            record_info['date'].strftime(self.RECORD_DATETIME_FORMAT))
        date_item.setData(QtCore.Qt.UserRole, record_info)

        dur_item = QtWidgets.QTableWidgetItem(
            helperutils.format_duration(record_info['duration']))
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

    def __selected_rows(self, selected_elems):
        return list(itertools.zip_longest(*([iter(selected_elems)] * 2)))
