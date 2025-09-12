import sys

from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtCore import QThread, Signal

from CSVManager.view.CSVView import CSVTableViewer
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

    def __init__(self):
        super().__init__()

    def _open_file(self):
        """
        Открытие файла.
        :return:
        """

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Открыть CSV файл с данными", "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            self._load_csv_file(file_name)

    def _load_csv_file(self, file_name):
        """
        Загрузка данных из CSV.
        :param file_name:
        :return:
        """
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"Загрузка файла: {file_name}")

        self.loader_thread = CSVLoaderNThread(file_name, 5)
        self.loader_thread.data_loaded.connect(self._on_data_loaded)
        self.loader_thread.error_message.connect(self._on_load_error)
        self.loader_thread.start()
    
    def _on_data_loaded(self, headers, data):
        super()._on_data_loaded(headers, data)
        self.x_col_combobox.addItems(headers)
        self.y_col_combobox.addItems(headers)

        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    window = CSVLoader()

    window.show()

    sys.exit(app.exec())
