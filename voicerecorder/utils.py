# -*- coding: utf-8 -*-

import datetime
import typing as t


def format_duration(duration: int) -> str:
    duration_delta = datetime.timedelta(milliseconds=duration)

    mm, ss = divmod(duration_delta.seconds, 60)
    hh, mm = divmod(mm, 60)

    s = "%d:%02d:%02d" % (hh, mm, ss)

    return s


def format_timestamp(timestamp: t.Union[int, float], fmt: str) -> str:
    return datetime.datetime.fromtimestamp(timestamp).strftime(f'{fmt}')
