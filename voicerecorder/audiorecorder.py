# -*- coding: utf-8 -*-

import os
import tempfile
import wave
import time
import shutil
import typing as t

import av

from PyQt5 import QtCore
from PyQt5 import QtMultimedia

from . import settings
from . import utils


class AudioRecord(QtCore.QObject):
    """Stores audio record info
    """

    def __init__(self, recorder: 'QtMultimedia.QAudioRecorder'):
        super().__init__(recorder)

        self._settings = settings.Settings(self)

        self._recorder = recorder
        self._recorder.setOutputLocation(self._make_temporary_wav())
        self._recorder.durationChanged.connect(self._update)

        self._filename = ''
        self._duration = 0
        self._timestamp = -1

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def timestamp(self) -> int:
        return self._timestamp

    def save(self, encoder):
        codec, ext = self._settings.get_audio_format()

        wav_fname = self._recorder.outputLocation().toLocalFile()
        out_fname = os.path.splitext(wav_fname)[0] + ext

        encoder(wav_fname, out_fname, codec)
        os.unlink(wav_fname)

        datetime_format = self._settings.get_record_filename_datetime_format()
        record_date_str = utils.format_timestamp(self.timestamp, datetime_format)

        _, ext = os.path.splitext(out_fname)
        fname = f'record-{record_date_str}{ext}'
        self._filename = os.path.join(self._settings.get_records_directory(), fname)

        shutil.move(out_fname, self.filename)

    def _update(self, duration):
        self._duration = duration
        self._timestamp = int(time.time())

    def _make_temporary_wav(self):
        tmp_records_dir = self._settings.get_temporary_records_directory()

        fd, fname = tempfile.mkstemp(prefix='record_', suffix='.wav', dir=tmp_records_dir)
        os.close(fd)
        return QtCore.QUrl.fromLocalFile(fname)


class AudioRecorder(QtCore.QObject):
    """Records audio
    """

    recording_progress = QtCore.pyqtSignal(int)
    encoding_started = QtCore.pyqtSignal()
    encoding_finished = QtCore.pyqtSignal()
    encoding_progress = QtCore.pyqtSignal(int)

    def __init__(self, parent: t.Optional[QtCore.QObject] = None):
        super().__init__(parent)

        self._settings = settings.Settings(self)

        self._recorder = QtMultimedia.QAudioRecorder(self)
        self._recorder.durationChanged.connect(lambda d: self.recording_progress.emit(d))

        self._record = None
        self._setup_recorder()

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

        self._record = AudioRecord(self._recorder)

        self._recorder.setAudioInput(audio_input)
        self._recorder.record()

    @property
    def record(self):
        return self._record

    def stop(self) -> t.Optional[AudioRecord]:
        if self._recorder.state() == QtMultimedia.QMediaRecorder.StoppedState:
            return

        self._recorder.stop()
        self._record.save(encoder=self._encode)

    def pause(self):
        if self._recorder.state() == QtMultimedia.QMediaRecorder.RecordingState:
            self._recorder.pause()

    def _setup_recorder(self):
        s = QtMultimedia.QAudioEncoderSettings()

        s.setCodec('')
        s.setSampleRate(48000)
        s.setBitRate(128000)
        s.setChannelCount(2)
        s.setQuality(QtMultimedia.QMultimedia.HighQuality)
        s.setEncodingMode(QtMultimedia.QMultimedia.ConstantQualityEncoding)

        self._recorder.setEncodingSettings(
            s, QtMultimedia.QVideoEncoderSettings(), '')

    def _encode(self, wav_fname: str, out_fname: str, codec: str):
        self.encoding_started.emit()

        inp = av.open(wav_fname, 'r')
        out = av.open(out_fname, 'w')

        ostream = out.add_stream(codec)

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
