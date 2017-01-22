# -*- coding: utf-8 -*-

"""
"""

import wave
import pyaudio as pa


class AudioRecorder:
    """Asynchronous audio recorder based on PyAudio
    """

    def __init__(self, fmt=pa.paInt16, channels=2, rate=44100, frames_per_buffer=1024):
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

        self.__stream = self.__audio.open(
            input=True,
            output=False,
            input_device_index=input_device_index,
            format=self.__format,
            channels=self.__channels,
            rate=self.__rate,
            frames_per_buffer=self.__frames_per_buffer,
            stream_callback=self.__record,
        )

    def stop(self):
        if self.__stream is None:
            return

        self.__status = pa.paComplete

        self.__stream.stop_stream()
        self.__stream.close()
        self.__stream = None

    def clear(self):
        self.__frames = b''
        self.__count_frames = 0
        self.__duration = 0

    def write_wav(self, filename: str):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.__channels)
            wf.setsampwidth(self.sample_size)
            wf.setframerate(self.__rate)
            wf.writeframes(self.__frames)

    def __record(self, data: bytes, frame_count, time_info, status):
        self.__frames += data
        self.__count_frames += 1
        self.__duration = (
            self.__count_frames / self.__rate * self.__frames_per_buffer)

        return data, self.__status
