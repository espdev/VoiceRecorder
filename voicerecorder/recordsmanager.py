from dataclasses import dataclass
from pathlib import Path
from shutil import which
import subprocess
import sys

from PySide6.QtCore import QEvent, QModelIndex, QObject, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QKeyEvent, QKeySequence
from PySide6.QtMultimedia import QMediaFormat
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide6.QtWidgets import QHeaderView, QMenu, QStyledItemDelegate, QTableView

from .settings import Settings
from .utils import format_audio_format, format_duration, format_timestamp


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


@dataclass
class Record:
    filename: str
    created: int
    duration: int
    audio_format: QMediaFormat


class RecordsManager(QObject):
    """Manages records"""

    def __init__(self, settings: Settings, records_view: QTableView, parent: QObject | None = None):
        super().__init__(parent)

        self._settings = settings
        self._records_view = records_view

        self._records_db = QSqlDatabase.addDatabase('QSQLITE', 'voicerecorder')
        self._setup_records_db()

        self._records_model = RecordsTableModel(self, self._records_db)
        self._setup_records_model()
        self._setup_records_view()

    def __del__(self):
        self.close()

    def eventFilter(self, obj, event):
        if not isinstance(obj, QTableView):
            return False
        if not isinstance(event, QKeyEvent):
            return False
        if event.type() != QEvent.Type.KeyPress:
            return False

        match event.key():
            case Qt.Key.Key_Escape:
                self._records_view.clearSelection()
                return True

            case Qt.Key.Key_Delete:
                self._delete_selected_records()
                return True

            case Qt.Key.Key_Space:
                self._play_record()
                return True

            case Qt.Key.Key_O | 0x429:
                self._open_recording_location()
                return True

        return False

    @property
    def records_model(self) -> QSqlTableModel:
        return self._records_model

    def add_record(self, record: Record):
        table_record = self._records_model.record()

        table_record.setValue('filename', record.filename)
        table_record.setValue('created', record.created)
        table_record.setValue('duration', record.duration)
        table_record.setValue('format', format_audio_format(record.audio_format))

        self._records_model.insertRecord(-1, table_record)
        self._submit_changes()

    def close(self):
        self._records_db.close()

    def _submit_changes(self):
        self._records_model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self._records_model.submitAll()
        self._records_model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)

    def _field_index(self, field: str) -> int:
        return self._records_model.fieldIndex(field)

    def _create_records_table(self) -> None:
        query = QSqlQuery(self._records_db)

        query.exec("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                created INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                format TEXT NOT NULL,
                description TEXT
            )
        """)

    def _setup_records_db(self):
        records_db_path = self._settings.records_db_path().as_posix()
        self._records_db.setDatabaseName(records_db_path)

        if not self._records_db.open():
            err = self._records_db.lastError()
            raise RuntimeError(f'Cannot open records database {records_db_path!r}: {err.driverText()}')

        self._create_records_table()

    def _setup_records_model(self):
        self._records_model.setTable('records')
        self._records_model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self._records_model.select()

        self._records_model.setHeaderData(self._field_index('id'), Qt.Orientation.Horizontal, self.tr('#'))
        self._records_model.setHeaderData(self._field_index('created'), Qt.Orientation.Horizontal, self.tr('Date'))
        self._records_model.setHeaderData(self._field_index('duration'), Qt.Orientation.Horizontal, self.tr('Duration'))
        self._records_model.setHeaderData(
            self._field_index('description'), Qt.Orientation.Horizontal, self.tr('Description')
        )

    def _setup_records_view(self) -> None:
        self._records_view.setModel(self._records_model)
        self._records_view.setSortingEnabled(True)
        self._records_view.setWordWrap(False)

        fields_to_hide = ['id', 'filename', 'format']

        for field in fields_to_hide:
            column_index = self._records_model.fieldIndex(field)
            self._records_view.setColumnHidden(column_index, True)

        self._records_view.horizontalHeader().setSectionResizeMode(
            self._field_index('created'), QHeaderView.ResizeMode.ResizeToContents
        )
        self._records_view.horizontalHeader().setSectionResizeMode(
            self._field_index('duration'), QHeaderView.ResizeMode.ResizeToContents
        )
        self._records_view.horizontalHeader().setSectionResizeMode(
            self._field_index('description'), QHeaderView.ResizeMode.Stretch
        )

        self._records_view.setItemDelegateForColumn(self._field_index('created'), DateDelegate(self._settings))
        self._records_view.setItemDelegateForColumn(self._field_index('duration'), DurationDelegate())

        self._records_view.doubleClicked.connect(self._play_record)
        self._records_view.installEventFilter(self)

        self._records_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._records_view.customContextMenuRequested.connect(self._show_records_context_menu)

    def _record_filename(self, row: int) -> str:
        return self._records_model.record(row).value('filename')

    def _play_record(self, index: QModelIndex = None):
        if index is None:
            index = self._records_view.currentIndex()
        filename = self._record_filename(index.row())
        QDesktopServices.openUrl(QUrl.fromLocalFile(filename))

    def _open_recording_location(self, index: QModelIndex | None = None):
        if not index:
            index = self._records_view.currentIndex()
        if not index.isValid():
            return

        filename = self._record_filename(index.row())

        if sys.platform == 'win32':
            file_managers = [
                ['explorer', f'/select,{Path(filename)}'],
            ]
        else:
            file_managers = [
                ['dolphin', '--select', filename],
                ['nautilus', '--select', filename],
                ['thunar', '--select', filename],
            ]

        for args in file_managers:
            if which(args[0]):
                try:
                    subprocess.run(args)
                    return
                except OSError:
                    continue

        location = Path(filename).parent.as_posix()
        QDesktopServices.openUrl(QUrl.fromLocalFile(location))

    def _delete_selected_records(self):
        indexes = self._records_view.selectionModel().selectedRows(0)
        rows = sorted([index.row() for index in indexes], reverse=True)

        for row in rows:
            Path(self._record_filename(row)).unlink(missing_ok=True)
            self._records_model.removeRow(row)

        self._submit_changes()

    def _show_records_context_menu(self, pos):
        index = self._records_view.indexAt(pos)
        if not index.isValid():
            return

        selected_indexes = self._records_view.selectionModel().selectedRows(0)
        menu = QMenu()

        if (selected_count := len(selected_indexes)) == 1:
            menu.addAction(
                self.tr('Open file location'), QKeySequence(Qt.Key.Key_O), lambda: self._open_recording_location(index)
            )
            menu.addAction(self.tr('Play record'), QKeySequence(Qt.Key.Key_Space), lambda: self._play_record(index))
            delete_text = self.tr('Delete record')
        else:
            delete_text = self.tr('Delete %n records', None, selected_count)

        menu.addAction(delete_text, QKeySequence(Qt.Key.Key_Delete), self._delete_selected_records)

        menu.exec(self._records_view.viewport().mapToGlobal(pos))
