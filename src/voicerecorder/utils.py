from datetime import datetime, timedelta

from PySide6.QtMultimedia import QMediaFormat


def format_duration(duration: int) -> str:
    duration_delta = timedelta(seconds=duration // 1000)
    return str(duration_delta)


def format_timestamp(timestamp: int | float, fmt: str) -> str:
    return datetime.fromtimestamp(timestamp).strftime(fmt)


def format_audio_format(audio_format: QMediaFormat) -> str:
    file_format = QMediaFormat.fileFormatName(audio_format.fileFormat())
    audio_codec = QMediaFormat.audioCodecName(audio_format.audioCodec())

    return f'{file_format}/{audio_codec}'
