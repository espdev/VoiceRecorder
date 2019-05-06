# -*- coding: utf-8 -*-

import functools

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from . import __app_name__
from . import __version__

from . import settings
from . import recordsmanager
from . import audiorecorder
from . import audiolevel
from . import statusinfo
from . import utils

from . import mainwindow_ui


class MainWindow(QtWidgets.QMainWindow):
    """Application MainWindow class
    """

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.ui = mainwindow_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self._level_monitors = [
            audiolevel.AudioLevelMonitor(self),
            audiolevel.AudioLevelMonitor(self),
        ]

        for levmon in self._level_monitors:
            levmon.setVisible(False)
            levmon.setMinimumWidth(50)
            levmon.setMaximumWidth(250)
            levmon.setFrameStyle(QtWidgets.QFrame.StyledPanel)

            self.ui.layoutAudioLevels.addWidget(levmon)

        self._recording_status_info = statusinfo.StatusInfo()
        self._recording_status_info.set_stop_status()

        status_bar: QtWidgets.QStatusBar = self.statusBar()
        status_bar.addWidget(self._recording_status_info)

        self.setWindowTitle(f'{__app_name__} - {__version__}')
        self.ui.labelRecordDuration.setVisible(False)

        self._settings = settings.Settings(self)

        self._audio_recorder = audiorecorder.AudioRecorder(self)

        self._audio_recorder.recording_progress.connect(self._on_update_duration_time)
        self._audio_recorder.encoding_progress.connect(self._recording_status_info.set_encoding_progress)
        self._audio_recorder.encoding_started.connect(self._recording_status_info.set_encode_status)
        self._audio_recorder.encoding_finished.connect(self._recording_status_info.set_stop_status)

        self._audio_levels_calculator = audiolevel.AudioLevelsCalculator(self, self._audio_recorder.recorder)
        self._audio_levels_calculator.levels_calculated.connect(self._on_show_audio_levels)

        self._records_manager = recordsmanager.RecordsManager(parent=self)

        self.ui.recordsTableView.setModel(self._records_manager.records_model)
        self.ui.recordsTableView.setSortingEnabled(True)

        self.ui.recordsTableView.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        self.ui.recordsTableView.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.ui.recordsTableView.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)

        self.ui.recordsTableView.doubleClicked.connect(self._on_play_record)
        self.ui.recordsTableView.selectionModel().selectionChanged.connect(self._on_change_selected_records)
        self.ui.recordsTableView.installEventFilter(self)

        self.ui.pbRecordingStartAndStop.toggled.connect(self._on_start_stop)
        self.ui.pbRecordingPause.toggled.connect(self._on_pause)
        self.ui.pbPlayRecords.clicked.connect(functools.partial(self._on_play_record, None))
        self.ui.pbRemoveRecords.clicked.connect(self._remove_selected_records)

        self._collect_audioinputs()
        self._read_settings()

    def closeEvent(self, event):
        self._write_settings()

    def eventFilter(self, obj, event: QtGui.QKeyEvent):
        if obj is not self.ui.recordsTableView:
            return False
        if event.type() != QtCore.QEvent.KeyPress:
            return False

        if event.key() == QtCore.Qt.Key_Delete:
            self._remove_selected_records()
            return True

        return False

    def _on_show_audio_levels(self, levels: list):
        for mon, level in zip(self._level_monitors, levels):
            mon.set_level(level)

    def _on_start_stop(self, is_checked):
        pb_title_text = {
            True: self.tr('Stop'),
            False: self.tr('Record'),
        }

        self.ui.pbRecordingStartAndStop.setText(pb_title_text[is_checked])
        self.ui.cmboxAudioInput.setEnabled(not is_checked)

        for levmon in self._level_monitors:
            levmon.setVisible(is_checked)

        self.ui.labelRecordDuration.setVisible(is_checked)

        if is_checked:
            self._start_recording()
        else:
            self._stop_recording()

    def _on_pause(self, is_checked):
        if is_checked:
            self._recording_status_info.set_pause_status()
            self._audio_recorder.pause()
        else:
            self._recording_status_info.set_record_status()
            self._audio_recorder.start()

    def _on_update_duration_time(self, duration):
        self.ui.labelRecordDuration.setText(utils.format_duration(duration))

    def _on_play_record(self, index: QtCore.QModelIndex = None):
        if index is None:
            index = self.ui.recordsTableView.selectionModel().selectedRows(0)[0]

        record = index.data(QtCore.Qt.UserRole)
        filename = record['filename'].replace('\\', '/')

        record_url = QtCore.QUrl(filename)
        QtGui.QDesktopServices.openUrl(record_url)

    def _on_change_selected_records(self):
        indexes = self.ui.recordsTableView.selectionModel().selectedRows(0)
        num_selected_rows = len(indexes)

        self.ui.pbRemoveRecords.setEnabled(num_selected_rows > 0)
        self.ui.pbPlayRecords.setEnabled(num_selected_rows == 1)

    def _start_recording(self):
        self._audio_recorder.start()
        self._recording_status_info.set_record_status()

        self.ui.pbRecordingStartAndStop.setIcon(QtGui.QIcon(':icons/stop'))

    def _stop_recording(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        try:
            self._audio_recorder.stop()
        except Exception as err:
            QtWidgets.QMessageBox.critical(self, 'Unable to save record', f'{err}')
        else:
            self._records_manager.add_record(self._audio_recorder.record)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        self._recording_status_info.set_stop_status()
        self._on_update_duration_time(0)

        self.ui.pbRecordingStartAndStop.setIcon(QtGui.QIcon(':icons/record'))

    def _collect_audioinputs(self):
        self.ui.cmboxAudioInput.addItem('Default', '')

        ainputs = self._audio_recorder.recorder.audioInputs()
        for ainput in ainputs:
            self.ui.cmboxAudioInput.addItem(ainput, ainput)

    def _read_settings(self):
        with self._settings.group('UI') as s:
            self.restoreGeometry(s.value('WindowGeometry', self.saveGeometry()))
            self.restoreState(s.value('WindowState', self.saveState()))

        with self._settings.group('Audio') as s:
            ainput = s.value('Input', 'Default')

        index = self.ui.cmboxAudioInput.findText(ainput)
        if index != -1:
            self.ui.cmboxAudioInput.setCurrentIndex(index)

    def _write_settings(self):
        with self._settings.group('UI') as s:
            s.setValue('WindowGeometry', self.saveGeometry())
            s.setValue('WindowState', self.saveState())

        with self._settings.group('Audio') as s:
            s.setValue('Input', self.ui.cmboxAudioInput.currentText())

    def _remove_selected_records(self):
        indexes = self.ui.recordsTableView.selectionModel().selectedRows(0)
        records = [index.data(QtCore.Qt.UserRole) for index in indexes]

        self._records_manager.remove_records(records)
        self._on_change_selected_records()
