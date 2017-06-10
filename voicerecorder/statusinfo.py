# -*- coding: utf-8 -*-
import math

from PyQt5 import QtWidgets, QtGui, QtCore


class StatusInfo(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._status_icon = QtWidgets.QLabel()
        self._status_icon.setPixmap(QtGui.QPixmap(':icons/rec'))

        self._status_icon_opacity = QtWidgets.QGraphicsOpacityEffect(
            self._status_icon)
        self._status_icon_opacity.setOpacity(1.0)

        self._status_icon.setGraphicsEffect(self._status_icon_opacity)

        self._status_text = QtWidgets.QLabel()

        self._encoding_progress = QtWidgets.QProgressBar()
        self._encoding_progress.setMinimum(0)
        self._encoding_progress.setMaximum(100)
        self._encoding_progress.setValue(0)
        self._encoding_progress.setTextVisible(False)
        self._encoding_progress.setMinimumWidth(200)
        self._encoding_progress.setMaximumHeight(22)
        self._encoding_progress.setVisible(False)

        self._animation_timer = QtCore.QTimer(self)
        self._animation_timer.setInterval(50)
        self._animation_timer.timeout.connect(self._animate_record_icon)

        self._opacity_dec = 0.1

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.addWidget(self._status_icon)
        self._layout.addWidget(self._status_text)
        self._layout.addWidget(self._encoding_progress)
        self._layout.setContentsMargins(9, 0, 9, 0)

        self.setLayout(self._layout)

    def set_record_status(self):
        self._status_text.setText(self.tr('Recording'))
        self._opacity_dec = abs(self._opacity_dec)
        self._animation_timer.start()
        self.setVisible(True)
        self._encoding_progress.setVisible(False)

    def set_pause_status(self):
        self._status_text.setText(self.tr('Paused'))
        self._animation_timer.stop()
        self._status_icon_opacity.setOpacity(0.5)
        self.setVisible(True)
        self._encoding_progress.setVisible(False)

    def set_stop_status(self):
        self._animation_timer.stop()
        self.setVisible(False)
        self._encoding_progress.setVisible(False)

    def set_encode_status(self):
        self._status_text.setText(self.tr('Encoding...'))
        self._animation_timer.stop()
        self._status_icon_opacity.setOpacity(0.5)
        self.setVisible(True)
        self._encoding_progress.reset()
        self._encoding_progress.setVisible(True)
        QtWidgets.QApplication.processEvents()

    def set_encoding_progress(self, value):
        self._encoding_progress.setValue(value)
        QtWidgets.QApplication.processEvents()

    def _animate_record_icon(self):
        opacity = round(
            self._status_icon_opacity.opacity() - self._opacity_dec, 2)

        if math.isclose(opacity, 0.0) or math.isclose(opacity, 1.0):
            self._opacity_dec = -self._opacity_dec

        self._status_icon_opacity.setOpacity(opacity)