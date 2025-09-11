import csv
import os

class Reader:
    def __init__(self, file_path, delimiter=None, encoding=None):
        """
        Конструктор ридера CSV файлов.

        :param file_path: Путь к файлу.
        :param delimiter:  Разделитель полей, для автоматического определения оставить None.
        :param encoding: Кодировка файла, для автоматического определения оставить None.
        """
        self.file_path = file_path
        self.delimiter = delimiter
        self.encoding = encoding
        self._detected_encoding = None
        self._detected_delimiter = None
        self._has_sep_line = False

    def detect_encoding(self, sample):
        """
        Определение кодировки.
        :param sample: Образец байтов.
        :return: Кодировки.
        """
        encodings_to_try = ['utf-8', 'cp1251', 'latin1', 'iso-8859-1', 'utf-16', 'utf-16le', 'utf-16be']
        for encoding in encodings_to_try:
            try:
                sample.decode(encoding)
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue
        return None

    def detect_delimiter(self, sample_text):
        """
        Определяет разделитель по текстовому образцу
        """
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample_text)
            return dialect.delimiter
        except csv.Error:
            # Альтернативный метод если Sniffer не сработал
            delimiters = [',', ';', '\t', '|']
            counts = {delim: sample_text.count(delim) for delim in delimiters}
            best_delim = max(counts, key=counts.get)
            return best_delim if counts[best_delim] > 0 else ','

    def auto_detect_parameters(self):
        """
        Автоматически определяет кодировку и разделитель
        """
        # Читаем первые 1024 байт файла
        with open(self.file_path, 'rb') as file:
            sample_bytes = file.read(1024)

        # Определяем кодировку
        if not self.encoding:
            self._detected_encoding = self.detect_encoding(sample_bytes) or 'utf-8'
        else:
            self._detected_encoding = self.encoding

        # Декодируем образец для анализа разделителя
        try:
            sample_text = sample_bytes.decode(self._detected_encoding)
        except UnicodeDecodeError:
            sample_text = sample_bytes.decode(self._detected_encoding, errors='ignore')

        lines = sample_text.splitlines()
        self._has_sep_line = False  # Сбрасываем флаг

        # Проверяем наличие строки с sep=
        if lines:
            first_line = lines[0].strip().lower()
            if first_line.startswith('sep='):
                self._has_sep_line = True
                # Извлекаем разделитель из строки
                sep_value = first_line[4:].strip()
                if sep_value:
                    self._detected_delimiter = sep_value[0]

        # Определяем разделитель, если не был задан и не найден в sep=
        if self.delimiter is not None:
            self._detected_delimiter = self.delimiter
        elif not hasattr(self, '_detected_delimiter') or self._detected_delimiter is None:
            if self._has_sep_line and len(lines) > 1:
                # Используем вторую строку для определения
                self._detected_delimiter = self.detect_delimiter(lines[1])
            elif lines:
                # Используем первую строку
                self._detected_delimiter = self.detect_delimiter(lines[0])
            else:
                self._detected_delimiter = ','

    def read(self):
        """
        Считывает CSV-файл и возвращает данные
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")

        # Автоматическое определение параметров
        self.auto_detect_parameters()

        try:
            with open(self.file_path, 'r', encoding=self._detected_encoding) as file:
                # Пропускаем строку с sep= при ее наличии
                if self._has_sep_line:
                    next(file)
                reader = csv.DictReader(file, delimiter=self._detected_delimiter)
                return list(reader)

        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении CSV: {str(e)}")


    # Пример использования

if __name__ == "__main__":
    reader = Reader('C:\\Users\\USER\\Desktop\\Python\\Scripts\\data\\deformation_19-06-2025-10-54-35_001_deformation_params.csv')

    try:
        data = reader.read()

        if data:
            print(f"Определенная кодировка: {reader._detected_encoding}")
            print(f"Определенный разделитель: {repr(reader._detected_delimiter)}")
            print(f"Заголовки: {list(data[0].keys())}")

            # Выводим первые 3 строки
            print("\nПервые строки данных:")
            for i, row in enumerate(data[:3], 1):
                print(f"Строка {i}: {row}")

    except Exception as e:
        print(f"Ошибка: {e}")