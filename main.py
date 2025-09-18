import sys

from PySide6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

from CSVLoader import CSVLoader


class GraphBuilder(QtWidgets.QMainWindow):

    _CSV_loader_window = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("График функций")
        self.resize(840, 840)
        self.setMinimumSize(840, 840)

        self._init_menu()

        # Создание центрального виджета и layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        # Виджет для панели управления
        control_widget = QtWidgets.QWidget()
        control_widget.setFixedWidth(110)
        control_layout = QtWidgets.QVBoxLayout(control_widget)
        control_layout.setContentsMargins(0,5,0,0)

        self._init_btn()

        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.build_median_btn)
        control_layout.addStretch()
        control_layout.setAlignment(QtCore.Qt.AlignCenter)

        main_layout.addWidget(control_widget)

        # Виджет для графиков
        self.graph_widget = pg.GraphicsLayoutWidget()
        main_layout.addWidget(self.graph_widget, 1)

        self.graphs = {}
        self.plot = None

        self.is_line = False
        self.color = "#ff0000"


    def _init_btn(self):
        """
        Инициализация кнопок на контрольной панели
        :return:
        """
        # Стиль кнопок

        btn_style = """
                QPushButton {
                    font-family: Regular;
                    font-size: 10px;
                }
                """

        # Кнопки управления
        self.build_median_btn = QtWidgets.QPushButton("Построить\n медиану")
        self.build_median_btn.setStyleSheet(btn_style)
        self.build_median_btn.setCheckable(True)
        self.build_median_btn.toggled.connect(self.build_median)
        self.build_median_btn.setFixedSize(100, 30)

        self.clear_btn = QtWidgets.QPushButton("Очистить")
        self.clear_btn.setStyleSheet(btn_style)
        self.clear_btn.pressed.connect(self.clear_graph)
        self.clear_btn.setFixedSize(100, 30)

    def _open_CSV_loader(self):
        if not self._CSV_loader_window:
            self._CSV_loader_window = CSVLoader()
            self._CSV_loader_window.cols_selected.connect(self._on_cols_selected)
            self._CSV_loader_window.is_line_checked.connect(self.set_is_lined)
            self._CSV_loader_window.color_selected.connect(self._on_color_selected)

        self._CSV_loader_window.show()
        self._CSV_loader_window.raise_()
        self._CSV_loader_window.activateWindow()

    def _init_menu(self):
        """
        Инициализация меню панели
        :return:
        """

        # Меню бар
        menu_bar = self.menuBar()
        menu_bar.setMinimumHeight(20)
        file_menu = menu_bar.addMenu("Файл")

        menu_bar.setStyleSheet("""
            QMenuBar {
                height: 20px;
            }
            QMenuBar::item {
                height: 20px;
                padding: 0px ;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #969696;
            }
            QMenuBar::item:pressed {
                background: #c0c0c0;
            }
        """)

        # Меню файла
        open_action = QtGui.QAction("Открыть", self)
        save_as_action = QtGui.QAction("Сохранить как ...", self)
        exit_action = QtGui.QAction("Выход", self)

        exit_action.triggered.connect(self.close)
        open_action.triggered.connect(self._open_CSV_loader)


        file_menu.addAction(open_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(exit_action)

    def _on_cols_selected(self, data, file_name, x_field, y_field):
        print(f"data: {data}")
        print(f"for x: {x_field}")
        print(f"for y: {y_field}")

        graph_key = file_name+x_field+y_field
        graph = []

        if not self.plot:
            self.plot = self.graph_widget.addPlot(titele=f"X = {x_field}"
                                         f"Y = {y_field}")
            self.plot.addLegend()
            self.plot.showGrid(x=True, y=True)


        x = [float(item[x_field].replace(",", ".")) for item in data]
        y = [float(item[y_field].replace(",", ".")) for item in data]

        if self.graphs.get(graph_key, False):

            if self.is_line:
                curve = self.plot.plot(pen=pg.mkPen(color=self.color, width=2), symbol='o')
                curve.setData(x, y)
                graph.append(curve)
            else:
                curve = self.plot.plot(pen=None, symbol='o')
                curve.setData(x, y)
                graph.append(curve)

        else:
            if self.is_line:
                curve = self.plot.plot(pen=pg.mkPen(color=self.color, width=2), symbol='o')

                curve.setData(x, y)

                graph.append(curve)
            else:
                curve = self.plot.plot(pen=None, symbol='o')

                curve.setData(x, y)

                graph.append(curve)

        self.graphs[file_name+x_field+y_field] = graph
        pass

    def set_is_lined(self, _is_lined):
        self.is_line = _is_lined

    def build_median(self):
        pass

    def clear_graph(self):
        if not self.graphs:
            return
        self.plot.clear()
        self.graphs = {}

    def _on_color_selected(self, color):
        self.color = color

    def closeEvent(self, event, /):
        super().closeEvent(event)
        if not self._CSV_loader_window:
            return
        self._CSV_loader_window.close()

if __name__ == "__main__":

    app = QtWidgets.QApplication.instance()

    if app is None:  # Если его нет,
        app = QtWidgets.QApplication(sys.argv)  # создаем новый

    app.setStyle("Fusion")


    window = GraphBuilder()
    window.show()
    app.exec()
