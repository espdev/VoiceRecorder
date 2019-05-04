# -*- coding: utf-8 -*-

import os
import tempfile
import wave
import time
import typing as t

import av

from PyQt5 import QtCore
from PyQt5 import QtMultimedia

from . import helperutils


class TemporaryRecord:

    def __init__(self, filename: str, duration: int, timestamp: int):
        self.filename = filename
        self.duration = duration
        self.timestamp = timestamp

    def __del__(self):
        if self.is_exist():
            os.unlink(self.filename)

    def is_exist(self):
        return os.path.isfile(self.filename)


class AudioRecorder(QtCore.QObject):
    """Records audio
    """

    recording_progress = QtCore.pyqtSignal(int)
    encoding_started = QtCore.pyqtSignal()
    encoding_finished = QtCore.pyqtSignal()
    encoding_progress = QtCore.pyqtSignal(int)

    def __init__(self, parent: t.Optional[QtCore.QObject] = None):
        super().__init__(parent)

        self._recorder = QtMultimedia.QAudioRecorder(self)
        self._recorder.durationChanged.connect(lambda d: self.recording_progress.emit(d))
        self._setup()

    @property
    def recorder(self) -> QtMultimedia.QAudioRecorder:
        return self._recorder

    def start(self, audio_input: str = ''):
        recorder_state = self._recorder.state()

        if recorder_state == QtMultimedia.QMediaRecorder.RecordingState:
            return
        elif recorder_state == QtMultimedia.QMediaRecorder.PausedState:
            self._recorder.record()
            return

        fd, fname = tempfile.mkstemp(prefix='record_', suffix='.wav',
                                     dir=helperutils.get_app_config_dir())
        os.close(fd)
        url = QtCore.QUrl.fromLocalFile(fname)

        self._recorder.setAudioInput(audio_input)
        self._recorder.setOutputLocation(url)
        self._recorder.record()

    def stop(self) -> t.Optional[TemporaryRecord]:
        if self._recorder.state() == QtMultimedia.QMediaRecorder.StoppedState:
            return

        duration = self._recorder.duration()
        self._recorder.stop()
        timestamp = int(time.time())

        # FIXME: move to a config
        encode_format = ('libvorbis', '.ogg')

        wav_fname = self._recorder.outputLocation().toLocalFile()
        out_fname = os.path.splitext(wav_fname)[0] + encode_format[1]

        self._encode(wav_fname, out_fname, encode_format[0])
        os.unlink(wav_fname)

        return TemporaryRecord(
            filename=out_fname,
            duration=duration,
            timestamp=timestamp
        )

    def pause(self):
        if self._recorder.state() == QtMultimedia.QMediaRecorder.RecordingState:
            self._recorder.pause()

    def _setup(self):
        settings = QtMultimedia.QAudioEncoderSettings()

        settings.setCodec('')
        settings.setSampleRate(48000)
        settings.setBitRate(128000)
        settings.setChannelCount(2)
        settings.setQuality(QtMultimedia.QMultimedia.HighQuality)
        settings.setEncodingMode(QtMultimedia.QMultimedia.ConstantQualityEncoding)

        self._recorder.setEncodingSettings(
            settings, QtMultimedia.QVideoEncoderSettings(), '')

    def _encode(self, wav_fname, out_fname, fmt):
        self.encoding_started.emit()

        inp = av.open(wav_fname, 'r')
        out = av.open(out_fname, 'w')

        ostream = out.add_stream(fmt)

        with wave.open(wav_fname, 'rb') as wav:
            num_frames = wav.getnframes()

        num_encoded_frames = 0

        for frame in inp.decode(audio=0):
            frame.pts = None

            for p in ostream.encode(frame):
                out.mux(p)

            num_encoded_frames += frame.samples
            progress_value = int(100 * num_encoded_frames / num_frames)

            self.encoding_progress.emit(progress_value)

        for p in ostream.encode(None):
            out.mux(p)

        out.close()
        self.encoding_finished.emit()
