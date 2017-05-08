# -*- coding: utf-8 -*-

"""
"""

import array

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtMultimedia


class AudioBufferProcessor(QtCore.QObject):
    """
    """

    buffer_processed = QtCore.pyqtSignal(list, str)

    def __init__(self, parent: QtCore.QObject=None,
                 source: QtMultimedia.QAudioRecorder=None):
        super().__init__(parent)

        self._data_type = ''
        self._data = []

        self._probe = QtMultimedia.QAudioProbe(self)
        self._probe.audioBufferProbed.connect(self._on_process_buffer)

        if source:
            self.set_source(source)

    def set_source(self, source: QtMultimedia.QAudioRecorder):
        self._probe.setSource(source)

    def data_type(self):
        return self._data_type

    def data(self):
        return self._data

    def _on_process_buffer(self, buffer: QtMultimedia.QAudioBuffer):
        self._data_type = ''
        self._data = []

        buffer_format = buffer.format()

        sample_type = buffer_format.sampleType()
        sample_size = buffer_format.sampleSize()

        buffer_type = {
            # Signed integer type
            (QtMultimedia.QAudioFormat.UnSignedInt, 8): 'B',
            (QtMultimedia.QAudioFormat.UnSignedInt, 16): 'H',
            (QtMultimedia.QAudioFormat.UnSignedInt, 32): 'I',

            # Unsigned integer type
            (QtMultimedia.QAudioFormat.SignedInt, 8): 'b',
            (QtMultimedia.QAudioFormat.SignedInt, 16): 'h',
            (QtMultimedia.QAudioFormat.SignedInt, 32): 'i',

            # Float type
            (QtMultimedia.QAudioFormat.Float, 32): 'f',

        }.get((sample_type, sample_size), None)

        if buffer_type is None:
            raise TypeError('Unknown buffer type {}'.format(sample_type))

        buffer_bytes = buffer.constData().asarray(buffer.byteCount())

        buffer_array = array.array(buffer_type)
        buffer_array.frombytes(buffer_bytes)

        ch_count = buffer_format.channelCount()
        data_by_channels = []

        for ch in range(ch_count):
            data_by_channels.append(buffer_array[ch::ch_count])

        self._data_type = buffer_type
        self._data = data_by_channels

        self.buffer_processed.emit(self._data, self._data_type)


class AudioLevelsCalculator(QtCore.QObject):
    """
    """

    levels_calculated = QtCore.pyqtSignal(list)

    def __init__(self, parent: QtCore.QObject=None,
                 source: QtMultimedia.QAudioRecorder=None):
        super().__init__(parent)

        self._levels = []

        self._buffer_processor = AudioBufferProcessor(self, source)
        self._buffer_processor.buffer_processed.connect(self._on_calc_levels)

    def set_source(self, source: QtMultimedia.QAudioRecorder=None):
        self._buffer_processor.set_source(source)

    def levels(self):
        return self._levels

    def _on_calc_levels(self, data: list, data_type: str):
        def calc_level(arr_data: array.array, arr_data_type: str):
            def calc_level_unsigned(value, peak_value):
                return abs(value - peak_value / 2) / (peak_value / 2)

            def calc_level_other(value, peak_value):
                return value / peak_value

            if arr_data_type == 'B':
                _peak_value = 2 ** 8 - 1
                _calc_level = calc_level_unsigned
            elif arr_data_type == 'H':
                _peak_value = 2 ** 16 - 1
                _calc_level = calc_level_unsigned
            elif arr_data_type == 'I':
                _peak_value = 2 ** 32 - 1
                _calc_level = calc_level_unsigned
            elif arr_data_type == 'b':
                _peak_value = 2 ** 7 - 1
                _calc_level = calc_level_other
            elif arr_data_type == 'h':
                _peak_value = 2 ** 15 - 1
                _calc_level = calc_level_other
            elif arr_data_type == 'i':
                _peak_value = 2 ** 31 - 1
                _calc_level = calc_level_other
            elif arr_data_type == 'f':
                _peak_value = 1.00003
                _calc_level = calc_level_other
            else:
                raise TypeError('Unsupported data type {}'.format(arr_data_type))

            max_value = max(map(abs, arr_data.tolist()))
            return _calc_level(max_value, _peak_value)

        levels = []

        for data_ch in data:
            level = calc_level(data_ch, data_type)
            levels.append(level)

        self._levels = levels
        self.levels_calculated.emit(levels)


class AudioLevelMonitor(QtWidgets.QFrame):
    """
    """

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                           QtWidgets.QSizePolicy.Fixed)

        self._level = 0.0

    def set_level(self, level: float):
        self._level = level
        self.update()

    def sizeHint(self):
        return QtCore.QSize(100, 10)

    def paintEvent(self, event: QtGui.QPaintEvent):
        width_level = self._level * self.width()
        windows_color = QtGui.QPalette().window()

        p = QtGui.QPainter(self)

        p.fillRect(0, 0, width_level, self.height(), QtCore.Qt.green)
        p.fillRect(width_level, 0, self.width(), self.height(), windows_color)

        self.drawFrame(p)
