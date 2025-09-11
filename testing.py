import sys
from PySide6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg


class GraphBuilder(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("График функций")
        self.resize(840, 840)
        self.setMinimumSize(840, 840)

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

        file_menu.addAction(open_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(exit_action)

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

        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.build_median_btn)
        control_layout.addStretch()
        control_layout.setAlignment(QtCore.Qt.AlignCenter)

        main_layout.addWidget(control_widget)

        # Виджет для графиков
        self.graph_widget = pg.GraphicsLayoutWidget()
        main_layout.addWidget(self.graph_widget, 1)

    def build_median(self):
        pass

    def clear_graph(self):
        pass

app = QtWidgets.QApplication(sys.argv)

app.setStyle("Fusion")


window = GraphBuilder()
window.show()
app.exec()
