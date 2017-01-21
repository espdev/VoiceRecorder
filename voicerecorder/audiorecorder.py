# -*- coding: utf-8 -*-

"""
"""

import wave
import pyaudio as pa


class AudioRecorder:
    """
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

    def __del__(self):
        self.stop_recording()
        self.__audio.terminate()

    @property
    def frames(self):
        return self.__frames

    @property
    def sample_size(self):
        return self.__audio.get_sample_size(self.__format)

    @property
    def is_recording(self):
        if self.__stream is None:
            return False
        return self.__stream.is_active()

    def start_recording(self, input_device_index=None):
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
            stream_callback=self.__record_callback,
        )

    def stop_recording(self):
        if self.__stream is None:
            return

        self.__status = pa.paComplete

        self.__stream.stop_stream()
        self.__stream.close()
        self.__stream = None

    def clear_recorded_frames(self):
        self.__frames = b''

    def write_wav(self, filename):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.__channels)
            wf.setsampwidth(self.sample_size)
            wf.setframerate(self.__rate)
            wf.writeframes(self.__frames)

    def __record_callback(self, data, frame_count, time_info, status):
        self.__frames += data
        return data, self.__status
