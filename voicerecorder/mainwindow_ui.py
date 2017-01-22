# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(567, 504)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pbRecordingStartAndStop = QtWidgets.QPushButton(self.centralwidget)
        self.pbRecordingStartAndStop.setCheckable(True)
        self.pbRecordingStartAndStop.setObjectName("pbRecordingStartAndStop")
        self.horizontalLayout.addWidget(self.pbRecordingStartAndStop)
        self.pbRecordingPause = QtWidgets.QPushButton(self.centralwidget)
        self.pbRecordingPause.setEnabled(False)
        self.pbRecordingPause.setCheckable(True)
        self.pbRecordingPause.setObjectName("pbRecordingPause")
        self.horizontalLayout.addWidget(self.pbRecordingPause)
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.labelRecordDuration = QtWidgets.QLabel(self.centralwidget)
        self.labelRecordDuration.setObjectName("labelRecordDuration")
        self.horizontalLayout.addWidget(self.labelRecordDuration)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gboxRecords = QtWidgets.QGroupBox(self.centralwidget)
        self.gboxRecords.setObjectName("gboxRecords")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.gboxRecords)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tableRecords = QtWidgets.QTableWidget(self.gboxRecords)
        self.tableRecords.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableRecords.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableRecords.setObjectName("tableRecords")
        self.tableRecords.setColumnCount(2)
        self.tableRecords.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableRecords.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRecords.setHorizontalHeaderItem(1, item)
        self.verticalLayout_2.addWidget(self.tableRecords)
        self.verticalLayout.addWidget(self.gboxRecords)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 567, 31))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.pbRecordingStartAndStop.toggled['bool'].connect(self.pbRecordingPause.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pbRecordingStartAndStop.setText(_translate("MainWindow", "Record"))
        self.pbRecordingPause.setText(_translate("MainWindow", "Pause"))
        self.labelRecordDuration.setText(_translate("MainWindow", "0:00:00"))
        self.gboxRecords.setTitle(_translate("MainWindow", "Records"))
        item = self.tableRecords.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Date"))
        item = self.tableRecords.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Duration"))

