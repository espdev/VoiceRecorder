# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

from voicerecorder import __version__

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'includes': ['atexit', 'PyQt5.QtNetwork'],
        'zip_include_packages': '*',
        'zip_exclude_packages': None,
    }
}

executables = [
    Executable('VoiceRecorder.pyw', base=base)
]

setup(
    name='VoiceRecorder',
    version=__version__,
    description='VoiceRecorder is a simple application for voice/audio record',
    options=options,
    executables=executables,
)
