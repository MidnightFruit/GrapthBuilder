import sys
from tkinter.font import names

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QApplication, QVBoxLayout, QWidget, QMainWindow, QComboBox


class ColorListModel(QAbstractListModel):

    def __init__(self, colors, parent=None):
        super().__init__()
        if colors and isinstance(colors[0], tuple) and len(colors[0]) == 2:
            self._colors = colors
        else:
            self._colors = [(color.name(), color) for color in colors]

    def rowCount(self, parent = QModelIndex()):
        return len(self._colors)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._colors):
            return None

        name, color = self._colors[index.row()]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return name
        elif role == Qt.DecorationRole:
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            return pixmap
        elif role == Qt.UserRole:
            return color

        return None

class ColorDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hover_color = QColor("#E0E0E0")

    def paint(self, painter: QPainter, option, index: QModelIndex):
        color = index.data(Qt.UserRole)
        display_text = index.data(Qt.DisplayRole)

        if color is None or display_text is None:
            super().paint(painter, option,index)
            return
        painter.save()

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlightedText().color() if option.state & QStyle.State_Active
            else option.palette.alternateBase())
            text_color = option.palette.highlightedText().color()
        else:
            painter.fillRect(option.rect, option.palette.base())
            text_color = option.palette.text().color()

        square_size = option.rect.height() - 6
        color_rect = option.rect.adjusted(3, 3, -(option.rect.width() - square_size - 3), -3)
        painter.fillRect(color_rect, color)
        painter.setPen(Qt.black)
        painter.drawRect(color_rect)

        text_rect = option.rect.adjusted(square_size+6,0,-3,0)
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, display_text)

        painter.restore()

    def sizeHint(self, option, index: QModelIndex):
        return QSize(120, 26)

class MainWindow(QMainWindow):
    """
    Пример основного окна с QComboBox для выбора цвета.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Выбор цвета для pyqtgraph")
        self.setGeometry(150, 150, 350, 120)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Определяем список цветов ---
        # Можно передавать просто QColor или пары (имя, QColor)
        self.colors = [
            ("Красный", QColor("red")),
            ("Зеленый", QColor("green")),
            ("Синий", QColor("blue")),
            ("Желтый", QColor("yellow")),
            ("Голубой", QColor("cyan")),
            ("Пурпурный", QColor("magenta")),
            ("Черный", QColor("black")),
            ("Белый", QColor("white")),
            ("Оранжевый", QColor("#FFA500")),
            ("Фиолетовый", QColor("#800080")),
            # QColor("gray"), # Пример добавления без имени
        ]

        # Создаем QComboBox
        self.color_combo = QComboBox()
        self.color_combo.setToolTip("Выберите цвет")

        # Создаем и устанавливаем модель
        self.color_model = ColorListModel(self.colors)
        self.color_combo.setModel(self.color_model)

        # Создаем и устанавливаем делегат
        self.color_delegate = ColorDelegate()
        self.color_combo.setItemDelegate(self.color_delegate)

        # Подключаем сигнал изменения выбора
        self.color_combo.currentIndexChanged.connect(self.on_color_selected)

        layout.addWidget(self.color_combo)

        # Устанавливаем начальный выбранный цвет
        self.color_combo.setCurrentIndex(2) # Синий по умолчанию

    def on_color_selected(self, index):
        """
        Обработчик события выбора цвета.
        """
        if index >= 0:
            # Получаем объект QColor из модели
            selected_color = self.color_model.data(
                self.color_model.index(index), Qt.UserRole
            )
            color_name = self.color_model.data(
                self.color_model.index(index), Qt.DisplayRole
            )
            if selected_color:
                # Выводим информацию о выбранном цвете
                print(f"Выбран цвет: {color_name} ({selected_color.name()})")
                # --- Здесь вы можете использовать selected_color для pyqtgraph ---
                # Например:
                # my_plot_item.setPen(selected_color) # Установить цвет линии
                # my_scatter_plot_item.setBrush(selected_color) # Установить цвет заливки точек

# --- Запуск приложения ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())