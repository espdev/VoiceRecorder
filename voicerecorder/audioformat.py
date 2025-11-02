from typing import Self
from dataclasses import dataclass
from functools import partial

from PySide6.QtCore import Signal
from PySide6.QtMultimedia import QMediaFormat
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMenu, QWidget

from .settings import Settings


@dataclass
class ItemInfo[T]:
    """Generic item with info"""

    item: T
    name: str
    description: str


@dataclass
class AudioCodecInfo(ItemInfo[QMediaFormat.AudioCodec]):
    """Audio codec with info"""

    @classmethod
    def from_audio_codec(cls, audio_codec: QMediaFormat.AudioCodec) -> Self:
        return cls(
            item=audio_codec,
            name=QMediaFormat.audioCodecName(audio_codec),
            description=QMediaFormat.audioCodecDescription(audio_codec),
        )


@dataclass
class FileFormatInfo(ItemInfo[QMediaFormat.FileFormat]):
    """File format with info"""

    @classmethod
    def from_file_format(cls, file_format: QMediaFormat.FileFormat) -> Self:
        return cls(
            item=file_format,
            name=QMediaFormat.fileFormatName(file_format),
            description=QMediaFormat.fileFormatDescription(file_format),
        )

    def supported_audio_codecs(
        self,
        mode: QMediaFormat.ConversionMode = QMediaFormat.ConversionMode.Encode,
    ) -> list[AudioCodecInfo]:
        """Get supported audio codecs for the file format"""

        media_format = QMediaFormat()
        media_format.setFileFormat(self.item)
        media_format.setAudioCodec(QMediaFormat.AudioCodec.Unspecified)
        media_format.setVideoCodec(QMediaFormat.VideoCodec.Unspecified)

        codecs = []
        for audio_codec in media_format.supportedAudioCodecs(mode):
            codecs.append(AudioCodecInfo.from_audio_codec(audio_codec))
        return codecs


class AudioFormatInfoLabel[T: ItemInfo](QLabel):
    item_changed: Signal

    def __init__(self, parent: QWidget | None = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._selected_item: T | None = None
        self._items: list[T] = []

    def set_items(self, items: list[T], selected_index: int = 0):
        if self._items == items:
            return
        self._items = items
        self.set_item(items[selected_index])

    def set_item(self, item: T):
        if item == self._selected_item:
            return
        if item not in self._items:
            return
        self._selected_item = item
        self.setText(item.name)
        self.item_changed.emit(item)

    def item(self) -> T | None:
        return self._selected_item

    def mouseReleaseEvent(self, event):
        menu = QMenu(self)

        for item_info in self._items:
            if item_info.name != item_info.description:
                name = f'{item_info.name} – {item_info.description}'
            else:
                name = item_info.name

            action = menu.addAction(name, partial(self.set_item, item_info))
            action.setCheckable(True)

            if item_info == self._selected_item:
                action.setChecked(True)

        menu.exec(event.globalPosition().toPoint())
        super().mouseReleaseEvent(event)


class FileFormatLabel(AudioFormatInfoLabel[FileFormatInfo]):
    item_changed = Signal(FileFormatInfo)


class AudioCodecLabel(AudioFormatInfoLabel[AudioCodecInfo]):
    item_changed = Signal(AudioCodecInfo)


class AudioFormat(QWidget):
    """AudioFormat widget to manipulate audio file formats and codecs"""

    audio_format_changed = Signal(QMediaFormat, str)

    audio_file_formats = {
        QMediaFormat.FileFormat.Mpeg4Audio: '.mp4a',
        QMediaFormat.FileFormat.Matroska: '.mka',
        QMediaFormat.FileFormat.Ogg: '.oga',
        QMediaFormat.FileFormat.Wave: '.wav',
        QMediaFormat.FileFormat.WMA: '.wma',
        QMediaFormat.FileFormat.MP3: '.mp3',
        QMediaFormat.FileFormat.AAC: '.aac',
        QMediaFormat.FileFormat.FLAC: '.flac',
    }

    def __init__(self, settings: Settings, parent: QWidget | None = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._settings = settings

        self._file_format_label = FileFormatLabel()
        self._file_format_label.setToolTip(self.tr('File format (container)'))

        self._audio_codec_label = AudioCodecLabel()
        self._audio_codec_label.setToolTip(self.tr('Audio codec'))

        self._set_file_formats_info()

        self._file_format_label.item_changed.connect(self._set_audio_codecs_info)
        self._file_format_label.item_changed.connect(self._on_change_audio_format)
        self._audio_codec_label.item_changed.connect(self._on_change_audio_format)

        self._separator_label = QLabel('/')

        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(5, 0, 5, 5)
        self._layout.addWidget(self._file_format_label)
        self._layout.addWidget(self._separator_label)
        self._layout.addWidget(self._audio_codec_label)

        self.setLayout(self._layout)

    def audio_format(self) -> tuple[QMediaFormat, str]:
        file_format = self._file_format_label.item()
        audio_codec = self._audio_codec_label.item()

        media_format = QMediaFormat()
        media_format.setFileFormat(file_format.item)
        media_format.setAudioCodec(audio_codec.item)
        media_format.setVideoCodec(QMediaFormat.VideoCodec.Unspecified)

        return media_format, self.audio_file_formats[file_format.item]

    def _set_file_formats_info(self):
        media_format = QMediaFormat()
        media_format.setFileFormat(QMediaFormat.FileFormat.UnspecifiedFormat)
        media_format.setAudioCodec(QMediaFormat.AudioCodec.Unspecified)
        media_format.setVideoCodec(QMediaFormat.VideoCodec.Unspecified)

        formats = []
        for file_format in media_format.supportedFileFormats(QMediaFormat.ConversionMode.Encode):
            if file_format in self.audio_file_formats:
                formats.append(FileFormatInfo.from_file_format(file_format))

        self._file_format_label.set_items(formats)
        self._set_audio_codecs_info(self._file_format_label.item())

        self._file_format_label.set_item(FileFormatInfo.from_file_format(self._settings.get_file_format()))
        self._audio_codec_label.set_item(AudioCodecInfo.from_audio_codec(self._settings.get_audio_codec()))

    def _set_audio_codecs_info(self, file_format_info: FileFormatInfo):
        codecs = file_format_info.supported_audio_codecs()
        self._audio_codec_label.set_items(codecs)

    def _on_change_audio_format(self):
        file_format = self._file_format_label.item()
        audio_codec = self._audio_codec_label.item()

        self._settings.set_file_format(file_format.item)
        self._settings.set_audio_codec(audio_codec.item)

        media_format = QMediaFormat()
        media_format.setFileFormat(file_format.item)
        media_format.setAudioCodec(audio_codec.item)
        media_format.setVideoCodec(QMediaFormat.VideoCodec.Unspecified)

        self.audio_format_changed.emit(media_format, self.audio_file_formats[file_format.item])
