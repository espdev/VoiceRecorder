# -*- coding: utf-8 -*-

import pathlib
from setuptools import setup


ROOT_DIR = pathlib.Path(__file__).parent


def get_version():
    about = {}
    ver_mod = ROOT_DIR / 'voicerecorder' / '_version.py'
    exec(ver_mod.read_text(), about)
    return about['__version__']


setup(
    name='VoiceRecorder',
    version=get_version(),
    packages=['voicerecorder'],
    url='',
    license='',
    author='Eugene Prilepin',
    author_email='',
    description='VoiceRecorder is a simple application for voice/audio record',
    install_requires=[
        'PyQt5',
        'tinydb',
        'av',
    ],
    entry_points={
        'gui_scripts': [
            'voicerecorder = voicerecorder.__main__:main',
        ],
        'console_scripts': [
            'voicerecorder_console = voicerecorder.__main__:main',
        ],
    },
)
