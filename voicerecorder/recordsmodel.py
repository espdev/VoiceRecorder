import typing as t

from PyQt5.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    QSortFilterProxyModel,
    Qt,
    QVariant,
)

from . import settings, utils

COLUMN_DATE = 0
COLUMN_DURATION = 1


class RecordsSortProxyModel(QSortFilterProxyModel):
    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        left_record = self.sourceModel().data(left, Qt.UserRole)
        right_record = self.sourceModel().data(right, Qt.UserRole)

        if left.column() == COLUMN_DATE:
            return left_record['timestamp'] < right_record['timestamp']

        elif left.column() == COLUMN_DURATION:
            return left_record['duration'] < right_record['duration']

        return False


class RecordsTableModel(QAbstractTableModel):
    """Records table model

    The model using TinyDB for storing records.
    """

    def __init__(self, parent: t.Optional[QObject] = None):
        super().__init__(parent)
        self._records = []
        self._record_count = 0
        self._settings = settings.Settings(self)
        self._table_dt_format = self._settings.get_record_table_datetime_format()

    def set_records(self, records: list):
        self.beginResetModel()
        self._records = records
        self._record_count = len(records)
        self.endResetModel()

    def rowCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        return self._record_count

    def columnCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        return 2

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> t.Any:
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            return {
                COLUMN_DATE: self.tr('Date'),
                COLUMN_DURATION: self.tr('Duration'),
            }.get(section, QVariant())

        if orientation == Qt.Vertical:
            return str(section + 1)

        return QVariant()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> t.Any:
        if not index.isValid():
            return QVariant()

        row = index.row()
        column = index.column()

        if row < 0 or row >= self._record_count:
            return QVariant()

        record = self._records[row]

        if role == Qt.DisplayRole:
            record_date = utils.format_timestamp(record['timestamp'], self._table_dt_format)
            record_duration = utils.format_duration(record['duration'])

            return {
                COLUMN_DATE: record_date,
                COLUMN_DURATION: record_duration,
            }.get(column, QVariant())

        if role == Qt.UserRole:
            return record

        return QVariant()
