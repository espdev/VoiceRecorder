# -*- coding: utf-8 -*-

"""
"""

import collections

import pyaudio as pa
from PyQt5 import QtCore


AudioRecord = collections.namedtuple(
    'AudioRecord', (
        'data',
        'duration',
        'count_frames',
        'format',
        'channels',
        'frame_rate',
        'frames_per_buffer',
        'sample_width',
    ))


class AudioRecorder(QtCore.QObject):
    """Asynchronous audio recorder based on PyAudio
    """

    record_updated = QtCore.pyqtSignal(float)

    def __init__(self, fmt=pa.paInt16, channels=2, rate=44100,
                 frames_per_buffer=1024, parent=None):
        super().__init__(parent=parent)

        self.__format = fmt
        self.__channels = channels
        self.__rate = rate
        self.__frames_per_buffer = frames_per_buffer

        self.__audio = pa.PyAudio()

        self.__stream = None
        self.__status = None

        self.__frames = b''
        self.__count_frames = 0
        self.__duration = 0.0

        self.__status_timer = QtCore.QTimer(self)
        self.__status_timer.setInterval(500)
        self.__status_timer.timeout.connect(self.__on_update_status)

    def __del__(self):
        self.stop()
        self.__audio.terminate()

    @property
    def frames(self):
        return self.__frames

    @property
    def count_frames(self):
        return self.__count_frames

    @property
    def duration(self):
        return self.__duration

    @property
    def sample_size(self):
        return self.__audio.get_sample_size(self.__format)

    @property
    def is_recording(self):
        if self.__stream is None:
            return False
        return self.__stream.is_active()

    def record(self, input_device_index=None):
        if self.__stream is not None:
            return

        self.__status = pa.paContinue
        self.__status_timer.start()

        self.__stream = self.__audio.open(
            input=True,
            output=False,
            input_device_index=input_device_index,
            format=self.__format,
            channels=self.__channels,
            rate=self.__rate,
            frames_per_buffer=self.__frames_per_buffer,
            stream_callback=self.__record_callback,
        )

    def stop(self):
        if self.__stream is None:
            return

        self.__status = pa.paComplete

        self.__stream.stop_stream()
        self.__stream.close()
        self.__stream = None
        self.__status_timer.stop()

    def clear(self):
        self.__frames = b''
        self.__count_frames = 0
        self.__duration = 0

    def get_record(self):
        return AudioRecord(
            data=self.frames,
            duration=self.duration,
            count_frames=self.count_frames,
            format=self.__format,
            channels=self.__channels,
            frame_rate=self.__rate,
            frames_per_buffer=self.__frames_per_buffer,
            sample_width=self.sample_size,
        )

    def __record_callback(self, data: bytes, frame_count, time_info, status):
        self.__frames += data
        self.__count_frames += 1
        self.__duration = (
            self.__count_frames / self.__rate * self.__frames_per_buffer)

        return data, self.__status

    def __on_update_status(self):
        self.record_updated.emit(self.__duration)
