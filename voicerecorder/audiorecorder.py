from typing import Self
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
import time

from PySide6.QtCore import QObject, Signal
from PySide6.QtMultimedia import (
    QAudioDevice,
    QAudioInput,
    QMediaCaptureSession,
    QMediaDevices,
    QMediaFormat,
    QMediaRecorder,
)

from .settings import Settings
from .types import ItemInfo
from .recordsmanager import Record


@dataclass
class AudioInputInfo(ItemInfo[QAudioDevice]):
    """Audio input with info"""

    @classmethod
    def from_audio_input(cls, audio_input: QAudioDevice) -> Self:
        return cls(
            item=audio_input,
            name=audio_input.id().toStdString(),
            description=audio_input.description(),
        )


def audio_inputs() -> list[AudioInputInfo]:
    inputs = []
    for audio_input in QMediaDevices.audioInputs():
        inputs.append(AudioInputInfo.from_audio_input(audio_input))
    return inputs


class AudioRecorder(QMediaRecorder):
    """Audio recorder"""

    recording_finished = Signal(Record)

    def __init__(self, settings: Settings, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._settings = settings

        self.setQuality(QMediaRecorder.Quality.HighQuality)
        self.setEncodingMode(QMediaRecorder.EncodingMode.ConstantQualityEncoding)

        self._audio_input = QAudioInput(QMediaDevices.defaultAudioInput(), self)

        self._media_capture_session = QMediaCaptureSession(self)
        self._media_capture_session.setAudioInput(self._audio_input)
        self._media_capture_session.setRecorder(self)

        self._suffix: str | None = None

        self.recorderStateChanged.connect(self._handle_state_change)

    def audio_input_info(self) -> AudioInputInfo:
        return AudioInputInfo(
            item=self._audio_input.device(),
            name=self._audio_input.device().id().toStdString(),
            description=self._audio_input.device().description(),
        )

    def set_audio_input(self, device: QAudioDevice) -> None:
        self._audio_input.deleteLater()
        self._audio_input = QAudioInput(device, self)
        self._media_capture_session.setAudioInput(self._audio_input)

    def set_audio_format(self, audio_format: QMediaFormat, suffix: str):
        self.setMediaFormat(audio_format)
        self._suffix = suffix

    def _handle_state_change(self, state: QMediaRecorder.RecorderState) -> None:
        match state:
            case QMediaRecorder.RecorderState.StoppedState:
                self._finish_recording()

    def _finish_recording(self):
        ts = time.time()
        datetime_format = self._settings.get_record_filename_format()
        record_name = datetime.fromtimestamp(ts).strftime(datetime_format)

        record_location = Path(self.actualLocation().toLocalFile())
        suffix = self._suffix or record_location.suffix

        new_record_location = self._settings.get_records_directory() / f'{record_name}{suffix}'
        new_record_location.parent.mkdir(parents=True, exist_ok=True)

        if new_record_location != record_location:
            shutil.move(record_location, new_record_location)

        self.recording_finished.emit(
            Record(
                filename=new_record_location.as_posix(),
                duration=self.duration(),
                timestamp=int(ts),
            )
        )
