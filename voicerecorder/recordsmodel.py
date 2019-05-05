# -*- coding: utf-8 -*-

import typing as t

import tinydb

from PyQt5.QtCore import (
    Qt,
    QObject,
    QAbstractTableModel,
    QModelIndex,
    QVariant,
)

from . import utils
from . import settings


class RecordsTableModel(QAbstractTableModel):
    """Records table model

    The model using TinyDB for storing records.
    """

    COLUMN_DATE = 0
    COLUMN_DURATION = 1

    def __init__(self, records_db: tinydb.TinyDB, parent: t.Optional[QObject] = None):
        super().__init__(parent)
        self._records_db = records_db
        self._settings = settings.Settings(self)

    def rowCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        return len(self._records_db)

    def columnCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        return 2

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> t.Any:
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            return {
                self.COLUMN_DATE: self.tr('Date'),
                self.COLUMN_DURATION: self.tr('Duration'),
            }.get(section, QVariant())

        if orientation == Qt.Vertical:
            return str(section + 1)

        return QVariant()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> t.Any:
        if not index.isValid():
            return QVariant()

        row = index.row()
        column = index.column()

        records = self._records_db.all()

        if row < 0 or row >= len(records):
            return QVariant()

        record = records[row]

        if role == Qt.DisplayRole:
            record_date = utils.format_timestamp(
                record['timestamp'], self._settings.get_record_table_datetime_format())
            record_duration = utils.format_duration(record['duration'])

            return {
                self.COLUMN_DATE: record_date,
                self.COLUMN_DURATION: record_duration,
            }.get(column, QVariant())

        if role == Qt.UserRole:
            return record

        return QVariant()
