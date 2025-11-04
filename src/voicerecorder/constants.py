from importlib.metadata import PackageNotFoundError, version

APP_NAME = 'VoiceRecorder'
PKG_NAME = 'voicerecorder'

try:
    APP_VERSION = version(PKG_NAME)
except PackageNotFoundError:  # pragma: no cover
    APP_VERSION = '0.0.0.dev0'

__version__ = APP_VERSION
