import math

from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QWidget

from .utils import format_duration


class StatusInfo(QWidget):
    def __init__(self, parent: QWidget | None = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._status_icon = QLabel()
        self._status_icon.setPixmap(QPixmap(':icons/rec'))
        self._status_icon_opacity = QGraphicsOpacityEffect(self._status_icon)
        self._status_icon_opacity.setOpacity(1.0)
        self._status_icon.setGraphicsEffect(self._status_icon_opacity)

        self._status_text = QLabel()
        self._duration_text = QLabel()

        self._animation_timer = QTimer(self)
        self._animation_timer.setInterval(50)
        self._animation_timer.timeout.connect(self._animate_icon)

        self._opacity_dec = 0.1

        self._layout = QHBoxLayout()
        self._layout.addWidget(self._status_icon)
        self._layout.addWidget(self._status_text)
        self._layout.addWidget(self._duration_text)
        self._layout.setContentsMargins(5, 0, 5, 5)

        self.setLayout(self._layout)

        self.set_stop_status()

    def set_record_status(self):
        self._status_text.setText(self.tr('Recording'))
        self.set_duration(0)
        self._opacity_dec = abs(self._opacity_dec)
        self._animation_timer.start()
        self.setVisible(True)

    def set_pause_status(self):
        self._status_text.setText(self.tr('Paused'))
        self._animation_timer.stop()
        self._status_icon_opacity.setOpacity(0.5)
        self.setVisible(True)

    def set_stop_status(self):
        self._animation_timer.stop()
        self._duration_text.setText('')
        self.setVisible(False)

    def set_duration(self, value: int):
        duration = format_duration(value)
        self._duration_text.setText(f'/  {duration}')

    def _animate_icon(self):
        opacity = round(self._status_icon_opacity.opacity() - self._opacity_dec, 2)

        if math.isclose(opacity, 0.0) or math.isclose(opacity, 1.0):
            self._opacity_dec = -self._opacity_dec

        self._status_icon_opacity.setOpacity(opacity)
