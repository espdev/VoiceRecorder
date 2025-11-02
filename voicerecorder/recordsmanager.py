from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QEvent, QModelIndex, QObject, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QKeyEvent
from PySide6.QtMultimedia import QMediaFormat
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide6.QtWidgets import QHeaderView, QTableView

from .recordsmodel import DateDelegate, DurationDelegate, RecordsTableModel
from .settings import Settings
from .utils import format_audio_format


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

        if event.key() == Qt.Key.Key_Delete:
            self._delete_selected_records()
            return True
        elif event.key() == Qt.Key.Key_Space:
            self._on_play_record()
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

        self._records_view.doubleClicked.connect(self._on_play_record)
        self._records_view.installEventFilter(self)

    def _record_filename(self, row: int) -> str:
        return self._records_model.record(row).value('filename')

    def _on_play_record(self, index: QModelIndex = None):
        if index is None:
            index = self._records_view.currentIndex()
        filename = self._record_filename(index.row())
        QDesktopServices.openUrl(QUrl(filename))

    def _delete_selected_records(self):
        indexes = self._records_view.selectionModel().selectedRows(0)
        rows = sorted([index.row() for index in indexes], reverse=True)

        for row in rows:
            Path(self._record_filename(row)).unlink(missing_ok=True)
            self._records_model.removeRow(row)

        self._submit_changes()
