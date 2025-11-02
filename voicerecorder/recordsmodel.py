from PySide6.QtCore import QObject, Qt
from PySide6.QtSql import QSqlTableModel
from PySide6.QtWidgets import QStyledItemDelegate

from .settings import Settings
from .utils import format_duration, format_timestamp


class DateDelegate(QStyledItemDelegate):
    def __init__(self, settings: Settings, parent: QObject | None = None):
        super().__init__(parent)
        self._settings = settings

    def displayText(self, value, locale):
        created = int(value)
        return format_timestamp(created, self._settings.record_table_format())

    def createEditor(self, parent, option, index):
        return None


class DurationDelegate(QStyledItemDelegate):
    def displayText(self, value, locale):
        duration = int(value)
        return format_duration(duration)

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter

    def createEditor(self, parent, option, index):
        return None


class RecordsTableModel(QSqlTableModel):
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.ToolTipRole and index.column() == self.fieldIndex('description'):
            return super().data(index, Qt.ItemDataRole.DisplayRole)

        return super().data(index, role)
