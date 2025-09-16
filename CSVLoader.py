import sys
import time

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QFileDialog, QComboBox, QPushButton, QLabel


from CSVManager.view.CSVView import CSVTableViewer, CSVLoaderThread
from CSVManager.Reader import Reader as CSVReader


class CSVLoaderNThread(QThread):
    """
    Поток для загрузки n-го количества строк из CSV файла.
    """

    data_loaded = Signal(list, list)
    error_message = Signal(str)

    def __init__(self, file_path, n):
        super().__init__()
        self.file_path = file_path
        self.delimiter = None
        self.encoding = None
        self.rows_to_load = n

    def run(self):
        try:
            reader = CSVReader(self.file_path)
            data = reader.read_n(self.rows_to_load)
            self.encoding = reader.encoding
            self.delimiter = reader.delimiter
            if data:
                headers = list(data[0].keys())
                rows = [list(row.values()) for row in data]
                self.data_loaded.emit(headers, rows)
            else:
                self.data_loaded.emit([],[])
        except Exception as e:
            self.error_message.emit(str(e))


class CSVLoader(CSVTableViewer):

    cols_selected = Signal(list)

    def __init__(self):
        super().__init__()
        self._init_selection_widget()

    def _open_file(self):
        """
        Открытие файла.
        :return:
        """

        self.file_name, _ = QFileDialog.getOpenFileName(
            self, "Открыть CSV файл с данными", "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if self.file_name:
            self._load_5_lines_from_csv_file(self.file_name)

    def _load_5_lines_from_csv_file(self, file_name):
        """
        Загрузка данных из CSV.
        :param file_name:
        :return:
        """
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"Загрузка файла: {file_name}")

        self.loader_5_thread = CSVLoaderNThread(file_name, 5)
        self.loader_5_thread.data_loaded.connect(self._on_data_loaded)
        self.loader_5_thread.error_message.connect(self._on_load_error)
        self.loader_5_thread.start()

    def _on_data_loaded(self, headers, data):
        super()._on_data_loaded(headers, data)

        self.x_col_combobox.clear()
        self.y_col_combobox.clear()

        self.x_col_combobox.addItems(headers)
        self.y_col_combobox.addItems(headers)

    def _init_selection_widget(self):

        self.y_col_combobox = QComboBox()
        self.x_col_combobox = QComboBox()

        self.x_col_combobox.setPlaceholderText("Выбор столбца x")
        self.y_col_combobox.setPlaceholderText("Выбор столбца y")

        self.build_graph_btn = QPushButton("Построить")
        self.build_graph_btn.setEnabled(False)

        self.info_layout.addWidget(QLabel("Ось X"))
        self.info_layout.addWidget(self.x_col_combobox)
        self.info_layout.addWidget(QLabel("Ось Y"))
        self.info_layout.addWidget(self.y_col_combobox)
        self.info_layout.addWidget(self.build_graph_btn)

        self.build_graph_btn.clicked.connect(self._load_csv_file)
        self.x_col_combobox.currentIndexChanged.connect(self._on_selection_changed)
        self.y_col_combobox.currentIndexChanged.connect(self._on_selection_changed)

    def build_graph(self, list):
        print("build")
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("")

        keys_to_build = [self.x_col_combobox.currentText(), self.y_col_combobox.currentText()]

        data_for_build = [{key: item[key] for key in keys_to_build} for item in list]
        self.cols_selected.emit(data_for_build)

    def _on_selection_changed(self):
        x_selection = self.x_col_combobox.currentIndex() >= 0
        y_selection = self.y_col_combobox.currentIndex() >= 0
        self.build_graph_btn.setEnabled(x_selection and y_selection)

    def _update_file_info(self, row_count, col_count):
        self.encoding_label.setText(f"Кодировка: {self.loader_5_thread.encoding}")
        self.delimiter_label.setText(f"Разделитель: {self.loader_5_thread.delimiter}")
        self.dimensions_label.setText(f"Строк: {row_count}, Столбцов: {col_count}")

    def set_solid_data(self, data: list):
        self._solid_data = data

    def _load_csv_file(self):
        """
        Загрузка данных из CSV файла.
        :param file_name: Путь к файлу.
        :return:
        """
        print("Loading csv")
        # Показать прогресс-бар
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"Загрузка файла: {self.file_name}")

        # Создать и запустить поток для загрузки CSV
        self.loader_thread = CSVLoaderThread(self.file_name, encoding=self.encoding)
        self.loader_thread.solid_data_loaded.connect(self.build_graph)
        self.loader_thread.start()
        while self.loader_thread.isRunning():
            print("waiting for finish")
            time.sleep(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    window = CSVLoader()

    window.show()

    sys.exit(app.exec())
