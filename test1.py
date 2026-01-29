import sys
from PySide6.QtWidgets import (
	QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
	QPushButton, QComboBox, QLineEdit, QCheckBox, QLabel,
	QSpinBox, QDoubleSpinBox, QFrame, QScrollArea, QGroupBox,
	QMessageBox, QListWidget, QSplitter, QGridLayout, QListWidgetItem
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QSizePolicy
from abc import ABC, abstractmethod


# --- Модель данных для параметра ---
class ParameterDefinition:
    def __init__(self, name, param_type, options=None, default_value=None, min_value=None, max_value=None, decimals=2):
        self.name = name
        self.param_type = param_type
        self.options = options or []
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.decimals = decimals


class ParameterWidget(QWidget):
    """Виджет для отображения и редактирования одного параметра."""

    def __init__(self, param_def: ParameterDefinition, parent=None):
        super().__init__(parent)
        self.param_def = param_def

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.name_label = QLabel(self.param_def.name + ":")
        layout.addWidget(self.name_label)

        self.value_widget = None
        self._create_value_widget()

        layout.addWidget(self.value_widget)

    def _create_value_widget(self):
        """Создает виджет для редактирования значения в зависимости от типа."""
        pdef = self.param_def
        if pdef.param_type == "ComboBox":
            self.value_widget = QComboBox()
            self.value_widget.addItems(pdef.options)
            if pdef.default_value is not None and isinstance(pdef.default_value, str):
                self.value_widget.setCurrentText(pdef.default_value)
            elif pdef.options:
                self.value_widget.setCurrentIndex(0)

        elif pdef.param_type == "Int":
            self.value_widget = QSpinBox()
            min_val = pdef.min_value if pdef.min_value is not None else -2147483648
            max_val = pdef.max_value if pdef.max_value is not None else 2147483647
            self.value_widget.setRange(min_val, max_val)
            if isinstance(pdef.default_value, int):
                self.value_widget.setValue(pdef.default_value)
            else:
                self.value_widget.setValue(0)

        elif pdef.param_type == "Float":
            self.value_widget = QDoubleSpinBox()
            min_val = pdef.min_value if pdef.min_value is not None else -sys.float_info.max
            max_val = pdef.max_value if pdef.max_value is not None else sys.float_info.max
            self.value_widget.setRange(min_val, max_val)
            self.value_widget.setDecimals(pdef.decimals)
            if isinstance(pdef.default_value, (int, float)):
                self.value_widget.setValue(float(pdef.default_value))
            else:
                self.value_widget.setValue(0.0)

        elif pdef.param_type == "Bool":
            self.value_widget = QCheckBox()
            if isinstance(pdef.default_value, bool):
                self.value_widget.setChecked(pdef.default_value)

        if self.value_widget is None:
            self.value_widget = QLabel(f"Неизвестный тип: {pdef.param_type}")

    def get_value(self):
        """Возвращает текущее значение параметра."""
        if isinstance(self.value_widget, QComboBox):
            return self.value_widget.currentText()
        elif isinstance(self.value_widget, QSpinBox):
            return self.value_widget.value()
        elif isinstance(self.value_widget, QDoubleSpinBox):
            return self.value_widget.value()
        elif isinstance(self.value_widget, QCheckBox):
            return self.value_widget.isChecked()
        else:
            return None

    def set_value(self, value):
        """Устанавливает значение параметра."""
        if isinstance(self.value_widget, QComboBox) and isinstance(value, str):
            self.value_widget.setCurrentText(value)
        elif isinstance(self.value_widget, QSpinBox) and isinstance(value, int):
            self.value_widget.setValue(value)
        elif isinstance(self.value_widget, QDoubleSpinBox) and isinstance(value, (int, float)):
            self.value_widget.setValue(float(value))
        elif isinstance(self.value_widget, QCheckBox) and isinstance(value, bool):
            self.value_widget.setChecked(value)


class ParameterManager(QWidget):
    """Виджет для управления группой параметров."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(2)
        self.container_layout.setContentsMargins(5, 5, 5, 5)

        self.scroll_area.setWidget(self.container_widget)
        self.layout.addWidget(self.scroll_area)

        self.param_widgets = {}

    def add_parameter(self, param_def: ParameterDefinition):
        """Программное добавление параметра в менеджер."""
        if param_def.name in self.param_widgets:
            print(f"Параметр с именем '{param_def.name}' уже существует.")
            return

        param_widget = ParameterWidget(param_def)
        self.container_layout.addWidget(param_widget)
        self.param_widgets[param_def.name] = param_widget

    def get_parameter_value(self, name):
        """Получить значение параметра по имени."""
        widget = self.param_widgets.get(name)
        if widget:
            return widget.get_value()
        return None

    def set_parameter_value(self, name, value):
        """Установить значение параметра по имени."""
        widget = self.param_widgets.get(name)
        if widget:
            widget.set_value(value)

    def get_all_values(self):
        """Получить словарь всех параметров и их значений."""
        return {name: widget.get_value() for name, widget in self.param_widgets.items()}


class ListManager(QWidget):
    """Виджет для отображения списка."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.list_label = QLabel("Список элементов:")
        self.layout.addWidget(self.list_label)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.items_data = []

    def add_item(self, text, data=None):
        """Добавляет элемент в список."""
        item = QListWidgetItem(text)
        self.list_widget.addItem(item)
        self.items_data.append(data if data is not None else text)

    def get_selected_item_data(self):
        """Возвращает данные выбранного элемента или None."""
        current_row = self.list_widget.currentRow()
        if 0 <= current_row < len(self.items_data):
            return self.items_data[current_row]
        return None


# --- Абстрактный интерфейс для источника данных (видео, изображения и т.д.) ---
class VideoSource(ABC):
    """Абстрактный класс для источника данных."""

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Возвращает QWidget, который будет отображаться в сетке или окне."""
        pass

    @abstractmethod
    def start(self):
        """Запускает источник (например, видеопоток)."""
        pass

    @abstractmethod
    def stop(self):
        """Останавливает источник."""
        pass

    @abstractmethod
    def save_frame(self):
        """Сохраняет текущий кадр/данные."""
        pass

    @abstractmethod
    def get_id(self):
        """Возвращает уникальный идентификатор источника."""
        pass

    # --- НОВЫЕ АБСТРАКТНЫЕ МЕТОДЫ ---
    @abstractmethod
    def pause(self):
        """Приостанавливает источник (например, видеопоток)."""
        pass

    @abstractmethod
    def resume(self):
        """Возобновляет источник (например, видеопоток)."""
        pass

    @abstractmethod
    def is_paused(self) -> bool:
        """Возвращает состояние паузы."""
        pass
    # ----------------------------


# --- Пример реализации для камеры (видео) ---
class CameraSource(VideoSource):
    """Конкретная реализация VideoSource для камеры."""

    def __init__(self, camera_id: str):
        self.camera_id = camera_id
        # Теперь используем QLabel для отображения
        self.widget = QLabel()
        self.widget.setAlignment(Qt.AlignCenter)
        self.widget.setStyleSheet("background-color: lightblue;")
        # Начальный текст
        self.widget.setText(f"Камера {self.camera_id}\n(Инициализация...)")
        self.timer = QTimer()
        self.frame_counter = 0
        self.timer.timeout.connect(self._update_frame)
        self._is_paused = False

    def get_widget(self) -> QWidget:
        return self.widget

    def start(self):
        print(f"Запуск камеры {self.camera_id}")
        self._is_paused = False
        self.timer.start(100)

    def stop(self):
        print(f"Остановка камеры {self.camera_id}")
        self.timer.stop()

    def pause(self):
        print(f"Пауза камеры {self.camera_id}")
        self._is_paused = True
        self.timer.stop()

    def resume(self):
        print(f"Возобновление камеры {self.camera_id}")
        self._is_paused = False
        self.timer.start(100)

    def is_paused(self) -> bool:
        return self._is_paused

    def save_frame(self):
        print(f"Сохранение кадра с камеры {self.camera_id}")

    def get_id(self):
        return self.camera_id

    def _update_frame(self):
        if not self._is_paused:
            self.frame_counter += 1
            self.widget.setText(f"Камера {self.camera_id}\nКадр: {self.frame_counter}")


# --- Пример реализации для изображения с зумом ---
class ImageSource(VideoSource):
    """Конкретная реализация VideoSource для изображения."""

    def __init__(self, image_path: str):
        self.image_path = image_path
        self.widget = QLabel(f"Изображение: {self.image_path}")
        self.widget.setAlignment(Qt.AlignCenter)
        self.widget.setStyleSheet("background-color: lightgreen;")
        self._is_paused = False # Для изображений пауза может быть условной

    def get_widget(self) -> QWidget:
        return self.widget

    def start(self):
        print(f"Загрузка изображения {self.image_path}")

    def stop(self):
        print(f"Остановка отображения изображения {self.image_path}")

    def pause(self):
        print(f"Пауза изображения {self.image_path} (условно)")
        self._is_paused = True

    def resume(self):
        print(f"Возобновление изображения {self.image_path} (условно)")
        self._is_paused = False

    def is_paused(self) -> bool:
        return self._is_paused

    def save_frame(self):
        print(f"Сохранение изображения {self.image_path}")

    def get_id(self):
        return self.image_path


# --- Виджет для отображения одного источника с кнопками ---
class SourceWidget(QWidget):
    """Обёртка для VideoSource с кнопками управления поверх виджета отображения."""

    def __init__(self, source: VideoSource, parent=None):
        super().__init__(parent)
        self.source = source

        # Основной layout для SourceWidget - QVBoxLayout
        # Он будет содержать ТОЛЬКО display_widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Убираем отступы

        # Получаем виджет отображения от источника
        self.display_widget = source.get_widget()
        # Добавляем его в layout - теперь он занимает всё пространство layout'а
        layout.addWidget(self.display_widget)

        # --- Создание кнопок ---
        # Кнопка сохранения кадра
        self.save_button = QPushButton("📸")
        self.save_button.setFixedSize(40, 40)
        self.save_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(0, 0, 0, 128); /* Полупрозрачный чёрный */
                color: white;
                border: 1px solid white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 150);
            }
            """
        )
        self.save_button.clicked.connect(self._on_save_clicked)

        # Кнопка паузы/воспроизведения
        self.pause_resume_button = QPushButton("⏸️")
        self.pause_resume_button.setFixedSize(40, 40)
        self.pause_resume_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(0, 0, 0, 128);
                color: white;
                border: 1px solid white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 150);
            }
            """
        )
        self.pause_resume_button.clicked.connect(self._on_pause_resume_clicked)

        # Устанавливаем SourceWidget как родителя для кнопок
        # Это делает их дочерними элементами SourceWidget,
        # но они НЕ добавляются в layout, а управляются через move()
        self.save_button.setParent(self)
        self.pause_resume_button.setParent(self)

        # Позиционируем кнопки поверх display_widget
        # Эти позиции можно будет изменить позже, например, через resizeEvent
        self.save_button.move(self.width() - self.save_button.width() - 10, 10)
        self.pause_resume_button.move(self.width() - self.pause_resume_button.width() - 10, self.save_button.y() + self.save_button.height() + 5)

    def resizeEvent(self, event):
        """Переопределяем событие изменения размера для обновления позиции кнопок."""
        super().resizeEvent(event)
        # Обновляем позиции кнопок при изменении размера SourceWidget
        # Пример: прижимаем к правому верхнему углу
        self.save_button.move(self.width() - self.save_button.width() - 10, 10)
        self.pause_resume_button.move(self.width() - self.pause_resume_button.width() - 10, self.save_button.y() + self.save_button.height() + 5)

    def _on_save_clicked(self):
        """Обработчик нажатия кнопки сохранения."""
        self.source.save_frame()

    def _on_pause_resume_clicked(self):
        """Обработчик нажатия кнопки паузы/воспроизведения."""
        if self.source.is_paused():
            self.source.resume()
            self.pause_resume_button.setText("⏸️") # Используем эмодзи
        else:
            self.source.pause()
            self.pause_resume_button.setText("▶️") # Используем эмодзи


# --- Менеджер для управления источниками (VideoManager) ---
class VideoManager(QWidget):
    """Управляет VideoSource: добавление, перемещение между сеткой и окнами."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll_area.setWidget(self.grid_container)

        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Словари для отслеживания
        self.sources = {}  # {id: VideoSource}
        self.widgets = {}  # {id: SourceWidget} - обёртки
        self.widgets_in_grid = {}  # {SourceWidget: (row, col, rowSpan, colSpan)}
        self.widgets_in_windows = {}  # {SourceWidget: VideoWindow}

    def add_source(self, source: VideoSource):
        """Добавляет источник в сетку (если его ещё нет)."""
        source_id = source.get_id()
        if source_id in self.sources:
            existing_widget = self.widgets[source_id]
            if existing_widget in self.widgets_in_windows:
                print(f"Источник {source_id} уже в окне, перемещаю в сетку.")
                self._move_widget_to_grid(existing_widget)
            else:
                print(f"Источник {source_id} уже в сетке.")
        else:
            print(f"Создаю новый SourceWidget для {source_id}")
            source_widget = SourceWidget(source)
            self.sources[source_id] = source
            self.widgets[source_id] = source_widget

            self._add_widget_to_grid(source_widget)
            source.start()

    def _add_widget_to_grid(self, source_widget):
        """Добавляет SourceWidget в сетку."""
        self.widgets_in_grid[source_widget] = (0, 0, 1, 1)
        self._rearrange_widgets()

    def _rearrange_widgets(self):
        """Переразмещает все виджеты в сетке."""
        current_count = len(self.widgets_in_grid)

        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                self.grid_layout.removeWidget(widget)
                widget.setParent(None)

        self.widgets_in_grid.clear()

        all_widgets_obj = list(self.widgets.values())

        if current_count == 1:
            only_widget = all_widgets_obj[0]
            self.grid_layout.addWidget(only_widget, 0, 0, 1, 1)
            self.widgets_in_grid[only_widget] = (0, 0, 1, 1)
            self.grid_layout.setRowStretch(0, 1)
            self.grid_layout.setColumnStretch(0, 1)
        else:
            import math
            cols = math.ceil(math.sqrt(current_count))
            rows = math.ceil(current_count / cols)

            for r in range(rows):
                self.grid_layout.setRowStretch(r, 1)
            for c in range(cols):
                self.grid_layout.setColumnStretch(c, 1)

            for index, w in enumerate(all_widgets_obj):
                row = index // cols
                col = index % cols
                self.grid_layout.addWidget(w, row, col, 1, 1)
                self.widgets_in_grid[w] = (row, col, 1, 1)

    def _remove_widget_from_grid(self, source_widget):
        """Удаляет SourceWidget из сетки."""
        print(f"  -> Удаляю SourceWidget из сетки")
        if source_widget in self.widgets_in_grid:
            self.grid_layout.removeWidget(source_widget)
            source_widget.setParent(None)
        source_id = source_widget.source.get_id()
        self.sources[source_id].stop()
        self._rearrange_widgets()

    def _move_widget_to_grid(self, source_widget):
        """Перемещает SourceWidget из окна в сетку."""
        print(f"Перемещаю SourceWidget из окна в сетку для {source_widget.source.get_id()}")
        window = self.widgets_in_windows[source_widget]
        layout = window.layout()
        layout.removeWidget(source_widget)
        del self.widgets_in_windows[source_widget]
        self.widgets_in_grid[source_widget] = (0, 0, 1, 1)
        self._rearrange_widgets()
        source_widget.source.start()

    def _move_widget_to_window(self, source_widget):
        """Перемещает SourceWidget из сетки в отдельное окно."""
        print(f"Перемещаю SourceWidget из сетки в окно для {source_widget.source.get_id()}")
        source_widget.source.stop()
        self._remove_widget_from_grid(source_widget)
        video_window = VideoWindow(source_widget, self) # Передаём VideoManager
        self.widgets_in_windows[source_widget] = video_window

        # Кнопка "В сетку" теперь в окне, но вызывает метод VideoManager
        video_window.back_to_grid_button.clicked.connect(
            lambda checked, sw=source_widget: self._move_widget_to_grid(sw)
        )

        video_window.show()


# --- Окно для отображения одного источника (VideoWindow) ---
class VideoWindow(QMainWindow):
    """Окно для отображения одного SourceWidget."""

    def __init__(self, source_widget: SourceWidget, manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Источник - {source_widget.source.get_id()}")
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Добавляем SourceWidget (с его кнопками) в layout центрального виджета
        layout.addWidget(source_widget)

        # --- НОВЫЙ: Горизонтальный layout для кнопок окна ---
        window_button_layout = QHBoxLayout()

        # Кнопка "В сетку" (теперь в окне)
        self.back_to_grid_button = QPushButton("Вернуть в сетку")
        window_button_layout.addWidget(self.back_to_grid_button)

        # Кнопка "Сохранить кадр" (дублирует кнопку из SourceWidget, можно убрать оттуда)
        self.save_frame_button = QPushButton("Сохранить кадр")
        self.save_frame_button.clicked.connect(source_widget._on_save_clicked)
        window_button_layout.addWidget(self.save_frame_button)

        # Кнопка "Пауза/Воспроизвести" (дублирует кнопку из SourceWidget, можно убрать оттуда)
        self.pause_resume_button = QPushButton("Пауза")
        # Связываем с методом SourceWidget
        self.pause_resume_button.clicked.connect(source_widget._on_pause_resume_clicked)
        # Обновляем текст кнопки при изменении состояния
        # source_widget.pause_resume_button.clicked.connect(self._update_pause_button_text) # Сложнее, нужно сложнее связывать
        # Проще обновлять текст при создании/изменении
        self._update_pause_button_text(source_widget.source.is_paused())
        # Связываем сигнал о смене состояния источника (если он будет)
        # source.source_state_changed.connect(self._update_pause_button_text) # Требует сигнала в VideoSource
        window_button_layout.addWidget(self.pause_resume_button)

        # Добавляем layout с кнопками окна в основной layout
        layout.addLayout(window_button_layout)

        self.setCentralWidget(central_widget)

        self.setMinimumSize(800, 600)
        screen = QApplication.primaryScreen().availableGeometry()
        window_width = int(screen.width() * 0.8)
        window_height = int(screen.height() * 0.8)
        self.resize(window_width, window_height)

        self.source_widget = source_widget
        self.manager = manager # Сохраняем ссылку на VideoManager

    def _update_pause_button_text(self, is_paused):
        """Обновляет текст кнопки паузы/воспроизведения."""
        if is_paused:
            self.pause_resume_button.setText("Воспроизвести")
        else:
            self.pause_resume_button.setText("Пауза")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Шаблон приложения с источниками")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_splitter = QSplitter(Qt.Horizontal)

        # Левая часть: параметры и список
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.list_manager = ListManager()
        self.list_manager.add_item("Камера 1", {"type": "camera", "id": "cam_1"})
        self.list_manager.add_item("Камера 2", {"type": "camera", "id": "cam_2"})
        self.list_manager.add_item("Камера 3", {"type": "camera", "id": "cam_3"})
        self.list_manager.add_item("Изображение 1", {"type": "image", "path": "path/to/image1.jpg"})
        self.list_manager.add_item("Изображение 2", {"type": "image", "path": "path/to/image2.png"})

        list_group = QGroupBox("Список источников")
        list_group_layout = QVBoxLayout()
        list_group_layout.addWidget(self.list_manager)
        list_group.setLayout(list_group_layout)

        self.param_definitions = [
            ParameterDefinition("Параметр 1", "ComboBox", options=["Опция A", "Опция B"], default_value="Опция A"),
            ParameterDefinition("Параметр 2", "Int", min_value=0, max_value=100, default_value=50),
        ]

        self.param_manager = ParameterManager()
        for param_def in self.param_definitions:
            self.param_manager.add_parameter(param_def)

        params_group = QGroupBox("Параметры")
        params_group_layout = QVBoxLayout()
        params_group_layout.addWidget(self.param_manager)
        params_group.setLayout(params_group_layout)

        self.demo_print_params_button = QPushButton("Печать параметров")
        self.demo_print_params_button.clicked.connect(self.demo_print_params)

        self.demo_print_list_button = QPushButton("Печать списка")
        self.demo_print_list_button.clicked.connect(self.demo_print_list)

        self.add_source_button = QPushButton("Добавить выбранный источник")
        self.add_source_button.clicked.connect(self.add_source)

        left_layout.addWidget(list_group)
        left_layout.addWidget(params_group)
        left_layout.addWidget(self.demo_print_params_button)
        left_layout.addWidget(self.demo_print_list_button)
        left_layout.addWidget(self.add_source_button)

        # Правая часть: источники (VideoManager)
        self.video_manager = VideoManager()
        video_group = QGroupBox("Источники (Сетка и Окна)")
        video_group_layout = QVBoxLayout()
        video_group_layout.addWidget(self.video_manager)
        video_group.setLayout(video_group_layout)

        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(video_group)

        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)

        main_layout.addWidget(main_splitter)

    def demo_print_params(self):
        all_values = self.param_manager.get_all_values()
        print("\n--- Текущие значения параметров ---")
        for name, value in all_values.items():
            print(f"  {name}: {value}")
        print("----------------------------------\n")

    def demo_print_list(self):
        selected_data = self.list_manager.get_selected_item_data()
        print(f"Выбранный элемент из списка: {selected_data}\n")

    def add_source(self):
        """Обработчик нажатия кнопки 'Добавить выбранный источник'."""
        selected_data = self.list_manager.get_selected_item_data()
        if selected_data is not None:
            source_type = selected_data.get("type")
            if source_type == "camera":
                source_id = selected_data.get("id")
                if source_id:
                    new_source = CameraSource(source_id)
                    self.video_manager.add_source(new_source)
            elif source_type == "image":
                image_path = selected_data.get("path")
                if image_path:
                    new_source = ImageSource(image_path)
                    self.video_manager.add_source(new_source)
            else:
                print(f"Неизвестный тип источника: {source_type}")
        else:
            QMessageBox.information(self, "Нет выбора", "Пожалуйста, выберите источник из списка.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
