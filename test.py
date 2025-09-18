import sys
import random
from PySide6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import numpy as np


class RealTimeGraph(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройка главного окна
        self.setWindowTitle("Реал-тайм графики с PyQtGraph")
        self.resize(1200, 800)

        # Создание центрального виджета и layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Создание виджета для графиков
        self.graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graph_widget)

        # Настройка панели управления
        control_panel = QtWidgets.QHBoxLayout()
        layout.addLayout(control_panel)

        # Кнопки управления
        self.pause_btn = QtWidgets.QPushButton("Пауза")
        self.pause_btn.setCheckable(True)
        self.pause_btn.toggled.connect(self.on_pause_toggled)
        control_panel.addWidget(self.pause_btn)

        self.clear_btn = QtWidgets.QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.on_clear_clicked)
        control_panel.addWidget(self.clear_btn)

        # Создание графиков
        self.setup_graphs()

        # Данные для графиков
        self.x = np.linspace(0, 10, 1000)
        self.y1 = np.zeros(1000)
        self.y2 = np.zeros(1000)
        self.y3 = np.zeros(1000)
        self.ptr = 0

        # Настройка таймеров
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(50)  # Обновление каждые 50 мс

        # Настройка стиля
        self.setup_styles()

    def setup_graphs(self):
        """Настройка графиков"""
        # Первый график - синусоида
        self.plot1 = self.graph_widget.addPlot(title="Синусоидальный сигнал")
        self.plot1.addLegend()
        self.plot1.showGrid(x=True, y=True)
        self.plot1.setLabel('left', 'Амплитуда', 'V')
        self.plot1.setLabel('bottom', 'Время', 's')
        self.curve1 = self.plot1.plot(pen=pg.mkPen('r', width=2), name="Синус")
        self.curve1a = self.plot1.plot(pen=pg.mkPen('g', width=1, style=QtCore.Qt.DashLine), name="Сглаженный")

        # Второй график - шум
        self.plot2 = self.graph_widget.nextRow()
        self.plot2 = self.graph_widget.addPlot(title="Случайный сигнал")
        self.plot2.showGrid(x=True, y=True)
        self.plot2.setLabel('left', 'Амплитуда', 'V')
        self.plot2.setLabel('bottom', 'Время', 's')
        self.curve2 = self.plot2.plot(pen=pg.mkPen('b', width=2))

        # Третий график - комбинированный
        self.plot3 = self.graph_widget.nextRow()
        self.plot3 = self.graph_widget.addPlot(title="Комбинированный сигнал")
        self.plot3.showGrid(x=True, y=True)
        self.plot3.setLabel('left', 'Амплитуда', 'V')
        self.plot3.setLabel('bottom', 'Время', 's')
        self.curve3 = self.plot3.plot(pen=pg.mkPen('y', width=2))

        # Регионы выбора на графике
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        self.plot3.addItem(self.region)
        self.region.sigRegionChanged.connect(self.update_region)

        # Перекрестие на всех графиках
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plot1.addItem(self.vLine, ignoreBounds=True)
        self.plot1.addItem(self.hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.plot1.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)

    def setup_styles(self):
        """Настройка стилей графиков"""
        # Установка темного фона
        self.graph_widget.setBackground('k')

        # Стиль сетки
        for plot in [self.plot1, self.plot2, self.plot3]:
            plot.getAxis('left').setPen('w')
            plot.getAxis('bottom').setPen('w')
            plot.getAxis('left').setTextPen('w')
            plot.getAxis('bottom').setTextPen('w')

        # Стиль кнопок
        btn_style = """
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3b3b3b;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: #3b3b3b;
            }
            QPushButton:checked {
                background-color: #5d5d5d;
            }
        """
        self.pause_btn.setStyleSheet(btn_style)
        self.clear_btn.setStyleSheet(btn_style)

    def update_data(self):
        """Обновление данных графиков"""
        if self.pause_btn.isChecked():
            return

        # Генерация новых данных
        t = self.ptr / 10.0
        noise = random.random() * 0.5

        # Обновление данных
        self.y1[:-1] = self.y1[1:]
        self.y2[:-1] = self.y2[1:]
        self.y3[:-1] = self.y3[1:]

        self.y1[-1] = np.sin(t) + noise
        self.y2[-1] = random.random() * 2 - 1
        self.y3[-1] = self.y1[-1] + self.y2[-1]

        # Обновление кривых
        self.curve1.setData(self.x, self.y1)
        self.curve2.setData(self.x, self.y2)
        self.curve3.setData(self.x, self.y3)

        # Сглаженная версия (скользящее среднее)
        smoothed = np.convolve(self.y1, np.ones(10) / 10, mode='same')
        self.curve1a.setData(self.x, smoothed)

        self.ptr += 1

    def update_region(self):
        """Обновление региона выбора"""
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.plot1.setXRange(minX, maxX, padding=0)

    def mouse_moved(self, event):
        """Обработка движения мыши для отображения перекрестия"""
        pos = event[0]
        if self.plot1.sceneBoundingRect().contains(pos):
            mousePoint = self.plot1.vb.mapSceneToView(pos)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

            # Обновление текста с координатами
            self.plot1.setTitle(f"<span style='font-size: 12pt'>X: {mousePoint.x():.2f}, \
                <span style='color: red'>Y1: {mousePoint.y():.2f}</span>")

    def on_pause_toggled(self, checked):
        """Обработка нажатия кнопки паузы"""
        self.pause_btn.setText("Возобновить" if checked else "Пауза")

    def on_clear_clicked(self):
        """Обработка нажатия кнопки очистки"""
        self.y1 = np.zeros(1000)
        self.y2 = np.zeros(1000)
        self.y3 = np.zeros(1000)
        self.ptr = 0


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Установка темной палитры для приложения
    app.setStyle('Fusion')
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    app.setPalette(dark_palette)

    window = RealTimeGraph()
    window.show()
    sys.exit(app.exec())