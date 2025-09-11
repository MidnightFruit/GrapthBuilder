import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, QHeaderView,
                               QFileDialog, QMessageBox, QMenu, QProgressBar, QStatusBar,
                               QVBoxLayout, QWidget, QLabel, QHBoxLayout, QSplitter,
                               QScrollArea, QSizePolicy)
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QSettings, QThread, Signal

# Импортируем ваш класс Reader с другим именем чтобы избежать конфликта
from CSVManager.Reader import Reader as CSVReader


class CSVLoaderThread(QThread):
    """Поток для загрузки CSV данных с использованием вашего Reader класса"""
    data_loaded = Signal(list, list)
    error_occurred = Signal(str)

    def __init__(self, file_path, delimiter=None, encoding=None):
        super().__init__()
        self.file_path = file_path
        self.delimiter = delimiter
        self.encoding = encoding

    def run(self):
        try:
            # Используем ваш CSVReader класс для чтения CSV
            reader = CSVReader(self.file_path, self.delimiter, self.encoding)
            data = reader.read()
            self.encoding = reader.encoding
            self.delimiter = reader.delimiter
            if data:
                # Извлекаем заголовки из первого элемента
                headers = list(data[0].keys())
                # Преобразуем данные в список списков для таблицы
                rows = [list(row.values()) for row in data]
                self.data_loaded.emit(headers, rows)
            else:
                self.data_loaded.emit([], [])

        except Exception as e:
            self.error_occurred.emit(str(e))


class CSVTableViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Просмотрщик CSV файлов")
        self.setGeometry(100, 100, 1200, 800)  # Увеличиваем размер окна

        # Настройки приложения
        self.settings = QSettings("MyCompany", "CSVViewer")

        # Создаем модель и таблицу
        self.model = QStandardItemModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # Настраиваем поведение заголовков столбцов
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # Изменено на Interactive
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionsMovable(True)  # Разрешаем перемещение столбцов
        self.table_view.setSortingEnabled(True)

        # Включаем горизонтальную прокрутку
        self.table_view.setHorizontalScrollMode(QTableView.ScrollPerPixel)

        # Создаем виджет для отображения информации о файле
        self.info_widget = QWidget()
        info_layout = QHBoxLayout()
        self.info_widget.setLayout(info_layout)

        self.encoding_label = QLabel("Кодировка: ")
        self.delimiter_label = QLabel("Разделитель: ")
        self.dimensions_label = QLabel("Размеры: ")

        info_layout.addWidget(self.encoding_label)
        info_layout.addWidget(self.delimiter_label)
        info_layout.addWidget(self.dimensions_label)
        info_layout.addStretch()

        # Основной контейнер
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.info_widget)

        # Создаем область прокрутки для таблицы
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_view)

        layout.addWidget(scroll_area)
        container.setLayout(layout)

        # Устанавливаем центральный виджет
        self.setCentralWidget(container)

        # Создаем меню и панель инструментов
        self._create_actions()
        self._create_menus()
        self._create_status_bar()

        # Загружаем настройки
        self._load_settings()

    def _create_actions(self):
        # Действие для открытия файла
        self.open_action = QAction("Открыть", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._open_file)

        # Действие для выхода
        self.exit_action = QAction("Выход", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

        # Действие для авто-подбора ширины столбцов
        self.resize_columns_action = QAction("Подогнать ширину столбцов", self)
        self.resize_columns_action.setShortcut("Ctrl+R")
        self.resize_columns_action.triggered.connect(self._resize_columns_to_contents)

    def _create_menus(self):
        # Меню Файл
        file_menu = self.menuBar().addMenu("Файл")
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Меню Вид
        view_menu = self.menuBar().addMenu("Вид")
        view_menu.addAction(self.resize_columns_action)


    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Прогресс-бар для отображения процесса загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def _load_settings(self):
        # Загрузка сохраненных настроек
        self.encoding = self.settings.value("encoding", None)

    def _save_settings(self):
        # Сохранение текущих настроек
        if hasattr(self, 'detected_encoding'):
            self.settings.setValue("encoding", self.detected_encoding)

    def _open_file(self):
        # Диалог выбора файла
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Открыть CSV файл", "",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_name:
            self._load_csv_file(file_name)

    def _load_csv_file(self, file_name):
        # Показать прогресс-бар
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"Загрузка файла: {file_name}")

        # Создать и запустить поток для загрузки CSV
        self.loader_thread = CSVLoaderThread(file_name, encoding=self.encoding)
        self.loader_thread.data_loaded.connect(self._on_data_loaded)
        self.loader_thread.error_occurred.connect(self._on_load_error)
        self.loader_thread.start()

    def _on_data_loaded(self, headers, data):
        # Обработка загруженных данных
        self.model.clear()

        # Установка заголовков
        self.model.setHorizontalHeaderLabels(headers)

        # Заполнение модели данными
        for row_data in data:
            items = [QStandardItem(str(cell)) for cell in row_data]
            self.model.appendRow(items)

        # Обновление информации о файле
        self._update_file_info(len(data), len(headers))

        # Обновление статусной строки
        self.status_bar.showMessage(
            f"Загружено {self.model.rowCount()} строк, {self.model.columnCount()} колонок"
        )
        self.progress_bar.setVisible(False)

        # Автоматически подгоняем ширину столбцов после загрузки
        self._resize_columns_to_contents()

    def _update_file_info(self, row_count, col_count):
        # Обновляем информацию о файле
        self.encoding_label.setText(f"Кодировка: {self.loader_thread.encoding}")
        self.delimiter_label.setText(f"Разделитель: {self.loader_thread.delimiter}")
        self.dimensions_label.setText(f"Строк: {row_count}, Столбцов: {col_count}")

    def _resize_columns_to_contents(self):
        # Подгоняем ширину столбцов под содержимое
        self.table_view.resizeColumnsToContents()

        # Если столбцы все еще не помещаются, устанавливаем минимальную ширину
        total_width = sum(self.table_view.columnWidth(i) for i in range(self.model.columnCount()))
        if total_width > self.table_view.width():
            # Устанавливаем режим, при котором столбцы можно прокручивать
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

    def _on_load_error(self, error_msg):
        # Обработка ошибок загрузки
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Ошибка загрузки",
                             f"Не удалось загрузить файл:\n{error_msg}")

    def contextMenuEvent(self, event):
        # Контекстное меню для таблицы
        context_menu = QMenu(self)

        copy_action = context_menu.addAction("Копировать")
        copy_action.triggered.connect(self._copy_selection)

        resize_action = context_menu.addAction("Подогнать ширину столбцов")
        resize_action.triggered.connect(self._resize_columns_to_contents)

        context_menu.exec_(event.globalPos())

    def _copy_selection(self):
        # Копирование выделенных данных
        selection = self.table_view.selectionModel()
        if selection.hasSelection():
            indexes = selection.selectedIndexes()
            if indexes:
                text = "\t".join(
                    index.data() for index in sorted(indexes, key=lambda i: (i.row(), i.column()))
                )
                QApplication.clipboard().setText(text)

    def resizeEvent(self, event):
        # При изменении размера окна пересчитываем размеры столбцов
        super().resizeEvent(event)
        if hasattr(self, 'model') and self.model.columnCount() > 0:
            self._resize_columns_to_contents()

    def closeEvent(self, event):
        # Сохранение настроек при закрытия
        self._save_settings()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle("Fusion")

    window = CSVTableViewer()
    window.show()

    sys.exit(app.exec())