import datetime

from PySide6.QtMultimedia import QMediaFormat


def format_duration(duration: int) -> str:
    duration_delta = datetime.timedelta(milliseconds=duration)

    mm, ss = divmod(duration_delta.seconds, 60)
    hh, mm = divmod(mm, 60)

    return f'{hh:d}:{mm:02d}:{ss:02d}'


def format_timestamp(timestamp: int | float, fmt: str) -> str:
    return datetime.datetime.fromtimestamp(timestamp).strftime(f'{fmt}')


def format_audio_format(audio_format: QMediaFormat) -> str:
    file_format = QMediaFormat.fileFormatName(audio_format.fileFormat())
    audio_codec = QMediaFormat.audioCodecName(audio_format.audioCodec())

    return f'{file_format}/{audio_codec}'
