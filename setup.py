# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='VoiceRecorder',
    version='0.5.0',
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
