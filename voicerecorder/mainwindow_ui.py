# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QTableView, QVBoxLayout, QWidget)
from . import mainwindow_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(475, 573)
        icon = QIcon()
        icon.addFile(u":/icons/mic", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.cmboxAudioInput = QComboBox(self.centralwidget)
        self.cmboxAudioInput.setObjectName(u"cmboxAudioInput")

        self.horizontalLayout_3.addWidget(self.cmboxAudioInput)

        self.horizontalLayout_3.setStretch(1, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pbRecordingStartAndStop = QPushButton(self.centralwidget)
        self.pbRecordingStartAndStop.setObjectName(u"pbRecordingStartAndStop")
        icon1 = QIcon()
        icon1.addFile(u":/icons/record", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pbRecordingStartAndStop.setIcon(icon1)
        self.pbRecordingStartAndStop.setIconSize(QSize(16, 16))
        self.pbRecordingStartAndStop.setCheckable(True)

        self.horizontalLayout.addWidget(self.pbRecordingStartAndStop)

        self.pbRecordingPause = QPushButton(self.centralwidget)
        self.pbRecordingPause.setObjectName(u"pbRecordingPause")
        self.pbRecordingPause.setEnabled(False)
        icon2 = QIcon()
        icon2.addFile(u":/icons/pause", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pbRecordingPause.setIcon(icon2)
        self.pbRecordingPause.setCheckable(True)

        self.horizontalLayout.addWidget(self.pbRecordingPause)

        self.horizontalSpacer = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.gboxRecords = QGroupBox(self.centralwidget)
        self.gboxRecords.setObjectName(u"gboxRecords")
        self.horizontalLayout_2 = QHBoxLayout(self.gboxRecords)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.recordsTableView = QTableView(self.gboxRecords)
        self.recordsTableView.setObjectName(u"recordsTableView")
        self.recordsTableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.recordsTableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.horizontalLayout_2.addWidget(self.recordsTableView)


        self.verticalLayout.addWidget(self.gboxRecords)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 475, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.pbRecordingStartAndStop.toggled.connect(self.pbRecordingPause.setEnabled)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Audio input:", None))
        self.pbRecordingStartAndStop.setText(QCoreApplication.translate("MainWindow", u"Record", None))
        self.pbRecordingPause.setText(QCoreApplication.translate("MainWindow", u"Pause", None))
        self.gboxRecords.setTitle(QCoreApplication.translate("MainWindow", u"Records", None))
    # retranslateUi

