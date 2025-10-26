import datetime


def format_duration(duration: int) -> str:
    duration_delta = datetime.timedelta(milliseconds=duration)

    mm, ss = divmod(duration_delta.seconds, 60)
    hh, mm = divmod(mm, 60)

    return f'{hh:d}:{mm:02d}:{ss:02d}'


def format_timestamp(timestamp: int | float, fmt: str) -> str:
    return datetime.datetime.fromtimestamp(timestamp).strftime(f'{fmt}')
