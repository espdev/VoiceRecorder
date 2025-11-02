from typing import Self
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
import time

from PySide6.QtCore import QByteArray, QObject, Signal
from PySide6.QtMultimedia import (
    QAudioDevice,
    QAudioInput,
    QMediaCaptureSession,
    QMediaDevices,
    QMediaFormat,
    QMediaRecorder,
)
from PySide6.QtWidgets import QApplication

from .recordsmanager import Record
from .settings import Settings


@dataclass
class AudioInputInfo:
    """Audio input with info"""

    device: QAudioDevice
    id: QByteArray
    description: str

    @classmethod
    def from_audio_device(cls, audio_device: QAudioDevice) -> Self:
        default_audio_device = QMediaDevices.defaultAudioInput()
        description = audio_device.description()

        if default_audio_device.id() == audio_device.id():
            default_label = QApplication.translate('AudioInput', 'Default')
            description = f'{audio_device.description()} [{default_label}]'

        return cls(
            device=audio_device,
            id=audio_device.id(),
            description=description,
        )

    @classmethod
    def from_id(cls, device_id: QByteArray) -> Self:
        audio_device = QMediaDevices.defaultAudioInput()

        for audio_input in QMediaDevices.audioInputs():
            if device_id == audio_input.id():
                audio_device = audio_input
                break

        return cls.from_audio_device(audio_device)

    @classmethod
    def default_audio_input(cls) -> Self:
        return cls.from_audio_device(QMediaDevices.defaultAudioInput())


def audio_inputs() -> list[AudioInputInfo]:
    """Get the list of all available audio inputs"""

    inputs = []

    for audio_input in QMediaDevices.audioInputs():
        inputs.append(AudioInputInfo.from_audio_device(audio_input))

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

        self.recorderStateChanged.connect(self._on_change_recorder_state)

    def audio_input_info(self) -> AudioInputInfo:
        return AudioInputInfo(
            device=self._audio_input.device(),
            id=self._audio_input.device().id(),
            description=self._audio_input.device().description(),
        )

    def set_audio_input(self, audio_input: AudioInputInfo) -> None:
        if audio_input.id == self._audio_input.device().id():
            return
        self._audio_input.deleteLater()
        self._audio_input = QAudioInput(audio_input.device, self)
        self._media_capture_session.setAudioInput(self._audio_input)

    def set_audio_format(self, audio_format: QMediaFormat, suffix: str):
        self.setMediaFormat(audio_format)
        self._suffix = suffix

    def _on_change_recorder_state(self, state: QMediaRecorder.RecorderState) -> None:
        match state:
            case QMediaRecorder.RecorderState.StoppedState:
                self._finish_recording()

    def _finish_recording(self):
        ts = time.time()
        datetime_format = self._settings.record_filename_format()
        record_name = datetime.fromtimestamp(ts).strftime(datetime_format)

        record_location = Path(self.actualLocation().toLocalFile())
        suffix = self._suffix or record_location.suffix

        new_record_location = self._settings.records_directory() / f'{record_name}{suffix}'
        new_record_location.parent.mkdir(parents=True, exist_ok=True)

        if new_record_location != record_location:
            shutil.move(record_location, new_record_location)

        self.recording_finished.emit(
            Record(
                filename=new_record_location.as_posix(),
                duration=self.duration(),
                created=int(ts),
                audio_format=QMediaFormat(self.mediaFormat()),
            )
        )
