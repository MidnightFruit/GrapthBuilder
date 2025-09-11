import sys

from PySide6.QtWidgets import QApplication, QFileDialog

from CSVManager.view.CSVView import CSVTableViewer


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
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    window = CSVLoader()

    window.show()

    sys.exit(app.exec())
