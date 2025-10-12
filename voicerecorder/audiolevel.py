import array

from PySide6.QtCore import QObject, QSize, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPalette
from PySide6.QtMultimedia import QAudioBuffer, QAudioFormat, QMediaRecorder
from PySide6.QtWidgets import QFrame, QPushButton, QSizePolicy


class AudioBufferProcessor(QObject):
    buffer_processed = Signal(list, str)

    def __init__(self, parent: QObject | None = None, source: QMediaRecorder | None = None):
        super().__init__(parent)

        self._data_type = ''
        self._data = []

        self._probe = QAudioProbe(self)
        self._probe.audioBufferProbed.connect(self._on_process_buffer)

        if source:
            self.set_source(source)

    def set_source(self, source: QMediaRecorder):
        self._probe.setSource(source)

    def data_type(self):
        return self._data_type

    def data(self):
        return self._data

    def _on_process_buffer(self, buffer: QAudioBuffer):
        self._data_type = ''
        self._data = []

        buffer_format = buffer.format()

        sample_type = buffer_format.sampleType()
        sample_size = buffer_format.sampleSize()

        buffer_type = {
            # Unsigned integer type
            (QAudioFormat.UnSignedInt, 8): 'B',
            (QAudioFormat.UnSignedInt, 16): 'H',
            (QAudioFormat.UnSignedInt, 32): 'I',
            # Signed integer type
            (QAudioFormat.SignedInt, 8): 'b',
            (QAudioFormat.SignedInt, 16): 'h',
            (QAudioFormat.SignedInt, 32): 'i',
            # Float type
            (QAudioFormat.Float, 32): 'f',
        }.get((sample_type, sample_size))

        if not buffer_type:
            raise TypeError(f'Unknown buffer type {(sample_type, sample_size)}')

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


class AudioLevelsCalculator(QObject):
    """ """

    levels_calculated = Signal(list)

    def __init__(self, parent: QObject | None = None, source: QMediaRecorder | None = None):
        super().__init__(parent)

        self._levels = []

        self._buffer_processor = AudioBufferProcessor(self, source)
        self._buffer_processor.buffer_processed.connect(self._on_calc_levels)

    def set_source(self, source: QMediaRecorder | None = None):
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
                _peak_value = 2**8 - 1
                _calc_level = calc_level_unsigned
            elif arr_data_type == 'H':
                _peak_value = 2**16 - 1
                _calc_level = calc_level_unsigned
            elif arr_data_type == 'I':
                _peak_value = 2**32 - 1
                _calc_level = calc_level_unsigned
            elif arr_data_type == 'b':
                _peak_value = 2**7 - 1
                _calc_level = calc_level_other
            elif arr_data_type == 'h':
                _peak_value = 2**15 - 1
                _calc_level = calc_level_other
            elif arr_data_type == 'i':
                _peak_value = 2**31 - 1
                _calc_level = calc_level_other
            elif arr_data_type == 'f':
                _peak_value = 1.00003
                _calc_level = calc_level_other
            else:
                raise TypeError(f'Unsupported data type {arr_data_type}')

            max_value = max(map(abs, arr_data.tolist()))
            return _calc_level(max_value, _peak_value)

        levels = []

        for data_ch in data:
            level = calc_level(data_ch, data_type)
            levels.append(level)

        self._levels = levels
        self.levels_calculated.emit(levels)


class AudioLevelMonitor(QFrame):
    """ """

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self._level = 0.0

    def set_level(self, level: float):
        self._level = level
        self.update()

    def sizeHint(self):
        btn = QPushButton()
        h = btn.sizeHint().height() / 2.6
        return QSize(100, h)

    def paintEvent(self, event: QPaintEvent):
        width_level = self._level * self.width()
        windows_color = QPalette().window()
        indicator_color = QColor(135, 211, 255)

        p = QPainter(self)

        p.fillRect(0, 0, width_level, self.height(), indicator_color)
        p.fillRect(width_level, 0, self.width(), self.height(), windows_color)

        self.drawFrame(p)
