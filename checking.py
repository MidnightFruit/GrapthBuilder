import sys
import random
import math # Добавлен для расчётов в OpenGLImageViewer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QCheckBox, QLabel,
    QSpinBox, QDoubleSpinBox, QFrame, QScrollArea, QGroupBox,
    QMessageBox, QListWidget, QListWidgetItem, QSplitter, QGridLayout, QDialog
)
from PySide6.QtCore import Qt, QTimer, QRect, QPoint, QSize  # QPoint добавлен для OpenGLImageViewer
from PySide6.QtGui import QImage, QPixmap, QColor, QPainter, QFont, QPalette, QMouseEvent, QWheelEvent # QMouseEvent, QWheelEvent добавлены для OpenGLImageViewer
from PySide6.QtWidgets import QSizePolicy
# --- ИМПОРТ QOpenGLWidget ---
from PySide6.QtOpenGLWidgets import QOpenGLWidget # Импортируем QOpenGLWidget отсюда
# ----------------------------


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


# --- Класс для имитации видеопотока (БУДЕТ УДАЛЁН) ---
# class VideoSimulator:
#     """Класс, который имитирует видеопоток, обновляя QLabel."""
#     # ... (удалён) ...


# --- Класс для имитации видеопотока (БУДЕТ УДАЛЁН) ---
# class VideoWidget:
#     """Виджет для отображения "видео" с одной камеры."""
#     # ... (удалён) ...


# --- Класс для имитации видеопотока (БУДЕТ УДАЛЁН) ---
# class VideoWindow:
#     """Окно для отображения одного VideoWidget."""
#     # ... (удалён) ...


# --- Добавленный OpenGLImageViewer ---
class OpenGLImageViewer(QOpenGLWidget):
    """QOpenGLWidget для отображения изображения с зумом и кнопками."""
    def __init__(self, image_paths, button_actions, parent=None):
        super().__init__(parent)
        self.image_paths = image_paths
        self.button_actions = button_actions # Список функций-действий для кнопок
        self.current_image_index = 0

        # --- Переменные состояния отображения ---
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.last_pos = QPoint() # Для панорамирования

        # --- Переменные для изображения ---
        self.texture_id = None
        self.image_width = 0
        self.image_height = 0
        self.opengl_image_loaded = False

        # --- Переменные для кнопок ---
        self.buttons = []
        # Создаём кнопки и их "границы" в мировых координатах
        # Мировые координаты будут соответствовать размеру изображения (0, 0) - (img_width, img_height)
        button_size_px = 60 # Размер кнопки в пикселях изображения
        num_buttons = len(self.button_actions)
        grid_size = int(math.ceil(math.sqrt(num_buttons)))

        for i in range(grid_size):
            for j in range(grid_size):
                index = i * grid_size + j
                if index < num_buttons:
                    # Рассчитываем позицию кнопки в мировых координатах (на изображении)
                    rel_x = (j + 0.5) / grid_size
                    rel_y = (i + 0.5) / grid_size
                    self.buttons.append({
                        'rel_x': rel_x,
                        'rel_y': rel_y,
                        'size_px': button_size_px,
                        'action': self.button_actions[index],
                        'rect': QRect(0, 0, 0, 0), # Будет рассчитано в update_button_rects
                        'text': f"Btn {index + 1}"
                    })

        # Загружаем первое изображение (если есть)
        if self.image_paths:
            self.load_image(self.image_paths[self.current_image_index])

    def load_image(self, path):
        """Загружает изображение в OpenGL текстуру."""
        # Очищаем старую текстуру
        if self.texture_id is not None:
            from OpenGL.GL import glDeleteTextures, glBindTexture, GL_TEXTURE_2D
            glDeleteTextures(1, [self.texture_id])
            self.opengl_image_loaded = False

        img = QImage(path)
        if img.isNull():
            print(f"Ошибка загрузки изображения: {path}")
            # Создаём заглушку
            img = self._create_placeholder_image(512, 512)

        # Преобразуем QImage в формат, подходящий для OpenGL
        img = img.rgbSwapped() # Qt: BGRA -> ARGB -> RGB(A) (последние 3 байта: R, G, B)
        data = img.bits().tobytes() # Получаем байты как bytes
        format_gl = GL_RGBA # После rgbSwapped() порядок R, G, B, A

        self.image_width = img.width()
        self.image_height = img.height()

        # Импортируем функции OpenGL
        from OpenGL.GL import glGenTextures, glBindTexture, glTexParameteri, GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE, GL_TEXTURE_WRAP_T, glTexImage2D, GL_UNSIGNED_BYTE, GL_RGBA

        # Генерируем ID текстуры
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        # Устанавливаем параметры текстуры
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # Загружаем данные изображения в текстуру
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, self.image_width, self.image_height,
            0, format_gl, GL_UNSIGNED_BYTE, data
        )

        # Сбрасываем привязку
        glBindTexture(GL_TEXTURE_2D, 0)

        # Устанавливаем начальный масштаб, чтобы изображение помещалось
        self.fit_image_to_view()

        # Обновляем позиции кнопок
        self.update_button_rects()

        self.opengl_image_loaded = True
        self.update() # Перерисовываем виджет

    def _create_placeholder_image(self, width, height):
        """Создаёт простую заглушку."""
        img = QImage(width, height, QImage.Format_RGBA8888)
        img.fill(Qt.lightGray)
        # Нарисуем текст
        from PySide6.QtGui import QPainter, QColor, QPen, QFont
        painter = QPainter(img)
        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont("Arial", 20))
        painter.drawText(img.rect(), Qt.AlignCenter, "Изображение\nне найдено")
        painter.end()
        return img

    def fit_image_to_view(self):
        """Устанавливает масштаб и смещение, чтобы изображение помещалось в виджет."""
        if not self.opengl_image_loaded:
            return

        # Размеры виджета
        widget_width = self.width()
        widget_height = self.height()

        # Соотношения сторон
        image_aspect = self.image_width / self.image_height
        widget_aspect = widget_width / widget_height

        if image_aspect > widget_aspect:
            # Изображение шире
            self.scale = widget_width / self.image_width
        else:
            # Изображение выше
            self.scale = widget_height / self.image_height

        # Центрируем
        self.offset_x = (widget_width - self.image_width * self.scale) / 2.0
        self.offset_y = (widget_height - self.image_height * self.scale) / 2.0

    def update_button_rects(self):
        """Обновляет QRect кнопок в координатах OpenGL (с учётом масштаба и смещения)."""
        if not self.opengl_image_loaded:
            return

        for btn_info in self.buttons:
            # Позиция центра кнопки в мировых координатах (на изображении)
            center_x = btn_info['rel_x'] * self.image_width
            center_y = btn_info['rel_y'] * self.image_height
            size = btn_info['size_px']

            # Позиция верхнего левого угла кнопки в мировых координатах
            top_left_x = center_x - size / 2
            top_left_y = center_y - size / 2

            # Преобразуем в координаты OpenGL (относительно сцены)
            btn_info['rect'] = QRect(
                int(top_left_x),
                int(top_left_y),
                int(size),
                int(size)
            )

    def initializeGL(self):
        """Инициализация OpenGL контекста."""
        from OpenGL.GL import glClearColor, glEnable, GL_TEXTURE_2D, GL_BLEND, glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
        glClearColor(0.0, 0.0, 0.0, 1.0) # Чёрный фон
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def resizeGL(self, width, height):
        """Вызывается при изменении размера виджета."""
        from OpenGL.GL import glViewport
        glViewport(0, 0, width, height)
        # Не пересчитываем масштаб здесь, если не хотим, чтобы изображение автоматически подстраивалось под размер окна
        # fit_image_to_view вызывается только при загрузке изображения или по специальному запросу
        self.update_button_rects() # Пересчитываем позиции кнопок при изменении размера

    def paintGL(self):
        """Отрисовка сцены."""
        from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glBindTexture, GL_TEXTURE_2D, glMatrixMode, GL_MODELVIEW, glLoadIdentity, glTranslatef, glScalef, glBegin, GL_QUADS, glTexCoord2f, glVertex2f, glEnd, glColor4f, glLineWidth, glBegin as glBegin_lines, GL_LINE_LOOP, glPopMatrix, GL_PROJECTION, glPushMatrix, glLoadIdentity as glLoadIdentity_proj, glOrtho
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.texture_id is not None and self.opengl_image_loaded:
            # --- Отрисовка изображения ---
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

            # Устанавливаем матрицу моделирования-вида-проекции
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # Сначала смещаем, потом масштабируем
            glTranslatef(self.offset_x, self.offset_y, 0.0)
            glScalef(self.scale, self.scale, 1.0)

            # Определяем вершины прямоугольника (в координатах изображения)
            x1, y1 = 0, 0
            x2, y2 = self.image_width, self.image_height

            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(x1, y1) # Левый верхний
            glTexCoord2f(1.0, 0.0); glVertex2f(x2, y1) # Правый верхний
            glTexCoord2f(1.0, 1.0); glVertex2f(x2, y2) # Правый нижний
            glTexCoord2f(0.0, 1.0); glVertex2f(x1, y2) # Левый нижний
            glEnd()

            glBindTexture(GL_TEXTURE_2D, 0) # Сбрасываем привязку

            # --- Отрисовка кнопок ---
            # Переключаемся в ортографическую проекцию, соответствующую размеру изображения
            glMatrixMode(GL_PROJECTION)
            glPushMatrix() # Сохраняем текущую матрицу
            glLoadIdentity_proj()
            # Устанавливаем ортографическую проекцию от (0, 0) до (image_width, image_height)
            glOrtho(0, self.image_width, self.image_height, 0, -1, 1) # Y вниз, как в Qt

            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()

            for btn_info in self.buttons:
                btn_rect = btn_info['rect']
                x, y, w, h = btn_rect.x(), btn_rect.y(), btn_rect.width(), btn_rect.height()

                # Цвет кнопки (RGBA: 0.0 - 1.0)
                glColor4f(0.0, 0.0, 0.0, 0.5) # Полупрозрачный чёрный

                glBegin(GL_QUADS)
                glVertex2f(x, y)
                glVertex2f(x + w, y)
                glVertex2f(x + w, y + h)
                glVertex2f(x, y + h)
                glEnd()

                # Рисуем границу
                glColor4f(1.0, 1.0, 1.0, 0.8) # Белая граница
                glLineWidth(1.0)
                glBegin_lines(GL_LINE_LOOP)
                glVertex2f(x, y)
                glVertex2f(x + w, y)
                glVertex2f(x + w, y + h)
                glVertex2f(x, y + h)
                glEnd()

            # Восстанавливаем матрицы
            glPopMatrix() # MODELVIEW
            glMatrixMode(GL_PROJECTION)
            glPopMatrix() # PROJECTION
            glMatrixMode(GL_MODELVIEW) # Возвращаемся к MODELVIEW

    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши."""
        if event.button() == Qt.LeftButton:
            # Преобразуем позицию мыши в координаты изображения (мировые)
            mouse_pos_widget = event.pos()
            img_x = (mouse_pos_widget.x() - self.offset_x) / self.scale
            img_y = (mouse_pos_widget.y() - self.offset_y) / self.scale

            # Проверяем попадание в кнопки
            for btn_info in self.buttons:
                btn_rect = btn_info['rect']
                if btn_rect.contains(int(img_x), int(img_y)):
                    # Нажата кнопка
                    btn_info['action']() # Вызываем привязанное действие
                    print(f"Нажата кнопка: {btn_info['text']}")
                    event.accept() # Поглощаем событие
                    return
        elif event.button() == Qt.MiddleButton:
            # Начало панорамирования
            self.last_pos = event.pos()
            event.accept()
            return

        # Если не нажата кнопка и не начато панорамирование, обработка по умолчанию
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Обработка движения мыши (для панорамирования)."""
        if event.buttons() & Qt.MiddleButton:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()

            # Изменяем смещение в зависимости от масштаба
            self.offset_x += dx / self.scale
            self.offset_y += dy / self.scale

            # Обновляем виджет для перерисовки
            self.update()

            # Обновляем позицию последнего нажатия
            self.last_pos = event.pos()
            event.accept()
            return

        # Если не панорамируем, обработка по умолчанию
        super().mouseMoveEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Обработка колеса мыши для зума."""
        # Получаем направление вращения
        delta = event.angleDelta().y()
        if delta == 0:
            event.ignore()
            return

        # Определяем коэффициент масштабирования
        factor = 1.2 if delta > 0 else 1 / 1.2

        # Получаем позицию курсора в координатах виджета
        mouse_pos_widget = event.position() # QPoint

        # Преобразуем позицию курсора в координаты изображения ДО изменения масштаба
        img_x_before = (mouse_pos_widget.x() - self.offset_x) / self.scale
        img_y_before = (mouse_pos_widget.y() - self.offset_y) / self.scale

        # Применяем масштабирование
        old_scale = self.scale
        self.scale *= factor

        # Ограничиваем масштаб
        min_scale = 0.1
        max_scale = 100.0
        self.scale = max(min_scale, min(max_scale, self.scale))

        # Рассчитываем новое смещение, чтобы позиция курсора в изображении осталась прежней
        self.offset_x = mouse_pos_widget.x() - (mouse_pos_widget.x() - self.offset_x) * self.scale / old_scale
        self.offset_y = mouse_pos_widget.y() - (mouse_pos_widget.y() - self.offset_y) * self.scale / old_scale

        # Обновляем виджет
        self.update()
        event.accept()

    def next_image(self):
        """Переходит к следующему изображению."""
        if self.image_paths:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
            self.load_image(self.image_paths[self.current_image_index])

    def previous_image(self):
        """Переходит к предыдущему изображению."""
        if self.image_paths:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_paths)
            self.load_image(self.image_paths[self.current_image_index])


# --- Функции-действия для кнопок OpenGLImageViewer ---
def action_1():
    print("Выполнено действие 1 (Кнопка 1)")

def action_2():
    print("Выполнено действие 2 (Кнопка 2)")

def action_3():
    print("Выполнено действие 3 (Кнопка 3)")

def action_4():
    print("Выполнено действие 4 (Кнопка 4)")

# --- Изменённый ImageManager (вместо VideoManager) ---
class ImageManager(QWidget):
    """Управляет OpenGLImageViewer: добавление, перемещение между сеткой и окнами."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Используем QScrollArea внутри ImageManager
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # <-- ВАЖНО: позволяет widget внутри растягиваться
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # Контейнер для сетки
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Устанавливаем политику размера для grid_container
        self.grid_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Устанавливаем контейнер в ScrollArea
        self.scroll_area.setWidget(self.grid_container)

        # Основной layout ImageManager теперь содержит только ScrollArea
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        # Устанавливаем политику размера для самого ImageManager
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Словари для отслеживания
        self.viewers = {}  # {camera_id: OpenGLImageViewer}
        self.viewers_in_grid = {}  # {OpenGLImageViewer: (row, col, rowSpan, colSpan)} - для отслеживания размещения
        self.viewers_in_windows = {}  # {OpenGLImageViewer: ImageWindow}

    def sizeHint(self):
        # Возвращаем минимальный размер, чтобы ImageManager (и QScrollArea внутри него)
        # могли растягиваться на всё доступное пространство
        return QSize(200, 150)  # Небольшой минимальный размер, можно изменить

    def add_image_set(self, image_set_id):
        """Добавляет набор изображений в сетку (если его ещё нет)."""
        if image_set_id in self.viewers:
            # Если уже есть, но в окне - переместим в сетку
            existing_viewer = self.viewers[image_set_id]
            if existing_viewer in self.viewers_in_windows:
                print(f"Набор изображений {image_set_id} уже в окне, перемещаю в сетку.")
                self._move_viewer_to_grid(existing_viewer)
            # Если уже в сетке - ничего не делаем
            else:
                print(f"Набор изображений {image_set_id} уже в сетке.")
        else:
            print(f"Создаю новый OpenGLImageViewer для набора {image_set_id}")
            # Создаём новый OpenGLImageViewer
            # Пути к изображениям и действия для кнопок
            # В реальном приложении пути будут зависеть от image_set_id
            image_paths = [
                # f"path/to/image_set_{image_set_id}_1.jpg",
                # f"path/to/image_set_{image_set_id}_2.png",
            ]
            button_actions = [action_1, action_2, action_3, action_4]
            image_viewer = OpenGLImageViewer(image_paths, button_actions)
            self.viewers[image_set_id] = image_viewer

            # Добавляем в сетку
            self._add_viewer_to_grid(image_viewer)

    def _add_viewer_to_grid(self, image_viewer):
        """Добавляет OpenGLImageViewer в сетку."""
        # <-- ИЗМЕНЕНО: Логика размещения теперь динамическая -->
        # Сначала добавляем новый виджет в словарь
        # Он будет добавлен в сетку позже, при переразмещении
        self.viewers_in_grid[image_viewer] = (0, 0, 1, 1)  # Временные значения

        # Переразмещаем все виджеты
        self._rearrange_viewers()

    def _rearrange_viewers(self):
        """Переразмещает все виджеты в сетке в зависимости от их количества."""
        current_count = len(self.viewers_in_grid)

        # Удаляем все виджеты из сетки перед переразмещением
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                self.grid_layout.removeWidget(widget)
                widget.setParent(None)

        # Очищаем словарь размещения
        self.viewers_in_grid.clear()

        # Список всех виджетов для переразмещения
        all_viewers = list(self.viewers.keys())
        all_viewers_obj = [self.viewers[image_set_id] for image_set_id in all_viewers]

        if current_count == 1:
            only_viewer = all_viewers_obj[0]
            self.grid_layout.addWidget(only_viewer, 0, 0, 1, 1)
            self.viewers_in_grid[only_viewer] = (0, 0, 1, 1)
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

            for index, v in enumerate(all_viewers_obj):
                row = index // cols
                col = index % cols
                self.grid_layout.addWidget(v, row, col, 1, 1)
                self.viewers_in_grid[v] = (row, col, 1, 1)

    def _remove_viewer_from_grid(self, image_viewer):
        """Удаляет OpenGLImageViewer из сетки."""
        print(f"  -> Удаляю OpenGLImageViewer из сетки")
        if image_viewer in self.viewers_in_grid:
            self.grid_layout.removeWidget(image_viewer)
            image_viewer.setParent(None)
            del self.viewers_in_grid[image_viewer]
        # Переразмещаем оставшиеся
        self._rearrange_viewers()

    def _move_viewer_to_grid(self, image_viewer):
        """Перемещает OpenGLImageViewer из окна в сетку."""
        print(f"Перемещаю OpenGLImageViewer из окна в сетку для набора {image_viewer}")
        # Удалить из окна
        window = self.viewers_in_windows[image_viewer]
        layout = window.layout()
        layout.removeWidget(image_viewer)
        del self.viewers_in_windows[image_viewer]
        # Добавить в сетку
        self.viewers_in_grid[image_viewer] = (0, 0, 1, 1)
        self._rearrange_viewers()

    def _move_viewer_to_window(self, image_viewer):
        """Перемещает OpenGLImageViewer из сетки в отдельное окно."""
        print(f"Перемещаю OpenGLImageViewer из сетки в окно")
        # Удалить из сетки (это вызовет переразмещение оставшихся)
        self._remove_viewer_from_grid(image_viewer)
        # Создать окно и добавить туда OpenGLImageViewer
        image_window = ImageWindow(image_viewer)
        self.viewers_in_windows[image_viewer] = image_window

        # Соединяем кнопку "В сетку" в окне
        image_window.back_to_grid_button.clicked.connect(
            lambda checked, iv=image_viewer: self._move_viewer_to_grid(iv)
        )

        # Показываем окно
        image_window.show()


# --- Изменённое ImageWindow (вместо VideoWindow) ---
class ImageWindow(QMainWindow):  # Используем QMainWindow вместо QDialog
    """Окно для отображения одного OpenGLImageViewer."""

    def __init__(self, image_viewer: OpenGLImageViewer, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Изображение - Набор")
        # self.setGeometry(200, 200, 400, 350)
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Добавляем OpenGLImageViewer в layout центрального виджета
        layout.addWidget(image_viewer)

        # Кнопка "В сетку" в окне
        self.back_to_grid_button = QPushButton("Вернуть в сетку")
        layout.addWidget(self.back_to_grid_button)

        # Устанавливаем центральный виджет
        self.setCentralWidget(central_widget)

        # Устанавливаем минимальный размер для всего окна
        self.setMinimumSize(800, 600)

        # Попробуем установить начальный размер (например, 80% от экрана)
        screen = QApplication.primaryScreen().availableGeometry()
        window_width = int(screen.width() * 0.8)
        window_height = int(screen.height() * 0.8)
        self.resize(window_width, window_height)

        self.image_viewer = image_viewer

    def closeEvent(self, event):
        """Обработчик закрытия окна - передаем сигнал родительскому ImageManager."""
        # Сигнал о закрытия окна, чтобы ImageManager мог вернуть виджет в сетку
        # if hasattr(self, 'on_window_closed'):
        #     self.on_window_closed.emit(self.image_viewer)
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Гибридное изображение (Сетка + Окна)")
        # self.setGeometry(100, 100, 1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Используем QSplitter для разделения левой (параметры/список) и правой (изображения) частей
        main_splitter = QSplitter(Qt.Horizontal)

        # Левая часть: параметры и список
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # --- Создание и заполнение ListManager (теперь сверху) ---
        self.list_manager = ListManager()

        # Пример: добавим элементы, представляющие "наборы изображений"
        self.list_manager.add_item("Набор 1", "Set1")
        self.list_manager.add_item("Набор 2", "Set2")
        self.list_manager.add_item("Набор 3", "Set3")
        self.list_manager.add_item("Набор 4", "Set4")
        self.list_manager.add_item("Набор 5", "Set5")

        list_group = QGroupBox("Список наборов")
        list_group_layout = QVBoxLayout()
        list_group_layout.addWidget(self.list_manager)
        list_group.setLayout(list_group_layout)

        # --- Создание и заполнение ParameterManager (теперь снизу) ---
        self.param_definitions = [
            ParameterDefinition("Режим работы", "ComboBox", options=["Автоматический", "Ручной", "Тестовый"],
                                default_value="Ручной"),
            ParameterDefinition("Количество потоков", "Int", min_value=1, max_value=16, default_value=4),
        ]

        self.param_manager = ParameterManager()
        for param_def in self.param_definitions:
            self.param_manager.add_parameter(param_def)

        params_group = QGroupBox("Параметры конфигурации")
        params_group_layout = QVBoxLayout()
        params_group_layout.addWidget(self.param_manager)
        params_group.setLayout(params_group_layout)

        # --- Кнопка для добавления выбранного набора ---
        self.add_image_set_button = QPushButton("Добавить выбранный набор")
        self.add_image_set_button.clicked.connect(self._on_add_image_set_clicked)

        # --- Кнопка для печати параметров ---
        self.demo_print_params_button = QPushButton("Печать параметров")
        self.demo_print_params_button.clicked.connect(self.demo_print_params)

        # Размещение элементов в левой части: Список (сверху), затем кнопки, затем Параметры (снизу)
        left_layout.addWidget(list_group)  # Список сверху
        left_layout.addWidget(self.add_image_set_button)  # Кнопка под списком
        left_layout.addWidget(self.demo_print_params_button)  # Кнопка под списком
        left_layout.addWidget(params_group)  # Параметры внизу

        # Правая часть: изображения (ImageManager)
        self.image_manager = ImageManager()  # ImageManager теперь сам содержит QScrollArea
        image_group = QGroupBox("Изображения (Сетка и Окна)")
        image_group_layout = QVBoxLayout()
        image_group_layout.addWidget(self.image_manager)  # Добавляем ImageManager напрямую
        image_group.setLayout(image_group_layout)

        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(image_group)

        main_splitter.setStretchFactor(0, 1)  # Левая часть
        main_splitter.setStretchFactor(1, 3)  # Правая часть

        main_layout.addWidget(main_splitter)

    def _on_add_image_set_clicked(self):
        """Обработчик нажатия кнопки 'Добавить выбранный набор'."""
        selected_set_id = self.list_manager.get_selected_item_data()
        if selected_set_id is not None:
            print(f"Добавление/перемещение изображений из набора {selected_set_id}")
            self.image_manager.add_image_set(selected_set_id)
        else:
            QMessageBox.information(self, "Нет выбора", "Пожалуйста, выберите набор изображений из списка.")

    def demo_print_params(self):
        """Демонстрация получения значений параметров."""
        all_values = self.param_manager.get_all_values()
        print("\n--- Текущие значения параметров ---")
        for name, value in all_values.items():
            print(f"  {name}: {value}")
        print("----------------------------------\n")

        msg_text = "\n".join([f"{name}: {value}" for name, value in all_values.items()])
        msg = QMessageBox()
        msg.setWindowTitle("Текущие значения параметров")
        msg.setText(msg_text)
        msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())