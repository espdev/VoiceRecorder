from pathlib import Path

from PySide6.QtCore import QEvent, QModelIndex, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QKeyEvent
from PySide6.QtWidgets import QHeaderView, QMainWindow, QStatusBar, QWidget

from . import mainwindow_ui, recordsmanager, settings
from .audioformat import AudioFormat
from .audiorecorder import AudioRecorder, audio_inputs
from .constants import APP_NAME, APP_VERSION
from .statusinfo import StatusInfo


class MainWindow(QMainWindow):
    """Application MainWindow class"""

    def __init__(self, parent: QWidget | None = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.ui = mainwindow_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f'{APP_NAME} - {APP_VERSION}')

        self._settings = settings.Settings(self)

        self._status_info = StatusInfo()
        self._audio_format = AudioFormat(self._settings)

        status_bar: QStatusBar = self.statusBar()
        status_bar.addWidget(self._status_info)
        status_bar.addPermanentWidget(self._audio_format)

        self._audio_recorder = AudioRecorder(self._settings, self)
        self._records_manager = recordsmanager.RecordsManager(self._settings, self)

        self._audio_format.audio_format_changed.connect(self._audio_recorder.set_audio_format)
        audio_format, suffix = self._audio_format.audio_format()

        self._audio_recorder.set_audio_format(audio_format, suffix)
        self._audio_recorder.durationChanged.connect(self._status_info.set_duration)
        self._audio_recorder.recording_finished.connect(self._records_manager.add_record)

        self.ui.recordsTableView.setModel(self._records_manager.records_model)
        self.ui.recordsTableView.setSortingEnabled(True)

        self.ui.recordsTableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.ui.recordsTableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        self.ui.recordsTableView.doubleClicked.connect(self._on_play_record)
        self.ui.recordsTableView.installEventFilter(self)

        self.ui.pbRecordingStartAndStop.toggled.connect(self._on_start_stop)
        self.ui.pbRecordingPause.toggled.connect(self._on_pause)

        self._collect_audioinputs()
        self._read_settings()

    def show(self):
        super().show()
        self.ui.recordsTableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def closeEvent(self, event):
        self._records_manager.close()
        self._write_settings()

    def eventFilter(self, obj, event: QKeyEvent):
        if obj is not self.ui.recordsTableView:
            return False
        if event.type() != QEvent.Type.KeyPress:
            return False

        if event.key() == Qt.Key.Key_Delete:
            self._remove_selected_records()
            return True

        return False

    def _on_start_stop(self, is_checked):
        pb_title_text = {
            True: self.tr('Stop'),
            False: self.tr('Record'),
        }

        self.ui.pbRecordingStartAndStop.setText(pb_title_text[is_checked])
        self.ui.cmboxAudioInput.setEnabled(not is_checked)

        if is_checked:
            self._start_recording()
        else:
            self._stop_recording()

        self._audio_format.setEnabled(not is_checked)

    def _on_pause(self, is_checked):
        if is_checked:
            self._status_info.set_pause_status()
            self._audio_recorder.pause()
        else:
            self._status_info.set_record_status()
            self._audio_recorder.record()

    def _on_play_record(self, index: QModelIndex = None):
        if index is None:
            index = self.ui.recordsTableView.selectionModel().selectedRows(0)[0]

        record = index.data(Qt.ItemDataRole.UserRole)
        filename = record['filename'].replace('\\', '/')

        record_url = QUrl(filename)
        QDesktopServices.openUrl(record_url)

    def _start_recording(self):
        self._audio_recorder.record()
        self._status_info.set_record_status()

        self.ui.pbRecordingStartAndStop.setIcon(QIcon(':icons/stop'))

    def _stop_recording(self):
        self._audio_recorder.stop()
        self._status_info.set_stop_status()
        self.ui.pbRecordingStartAndStop.setIcon(QIcon(':icons/record'))

    def _collect_audioinputs(self):
        for ainput in audio_inputs():
            self.ui.cmboxAudioInput.addItem(ainput.description, ainput.name)

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
        self._records_manager.remove_records(indexes)

    def _on_finish_recording(self, record) -> None:
        self._records_manager.add_record(record)
