import os
import logging  # Для логирования событий приложения
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QListWidgetItem, QLineEdit,
                             QLabel, QTabWidget, QFormLayout, QCheckBox, QComboBox,
                             QMessageBox, QSpinBox, QTextEdit, QScrollArea,
                             QGridLayout, QFrame, QFileDialog, QToolBar, QStatusBar,
                             QAbstractItemView, QDialog, QSpacerItem, QSizePolicy, QLayout, QCompleter)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings, QSize, QTimer, QRect, QPoint, QStringListModel
from PyQt6.QtGui import QPixmap, QAction, QIcon, QColor
from PyQt6.uic.properties import QtGui

from src.database import Recipe

# Настройка логирования для отслеживания событий приложения
logger = logging.getLogger(__name__)

from src.modules.recipe_dialog import RecipeDialog, RecipeCardDialog
from src.modules.settings_dialog import SettingsDialog
from src.modules.help_dialog import HelpDialog
from src.modules.add_ingredient_dialog import AddIngredientDialog

import sys
import os


def resource_path(relative_path):
    """Получает корректный путь к ресурсам в режиме exe и разработки"""
    try:
        # PyInstaller создает временную папку _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        try:
            # Альтернативный способ определения пути в PyInstaller
            base_path = os.path.join(sys._MEIPASS2, relative_path)
            if os.path.exists(base_path):
                return base_path
        except:
            # Режим разработки
            base_path = os.path.dirname(os.path.abspath(__file__))
            # Поднимаемся на уровень выше (из src в корень проекта)
            base_path = os.path.dirname(base_path)

    # Строим полный путь
    path = os.path.join(base_path, relative_path)

    # Проверяем наличие файла
    if os.path.exists(path):
        return path

    # Если не найден, пробуем альтернативные пути
    alternative_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path),
        os.path.join(os.getcwd(), relative_path),
        relative_path,
    ]

    for alt_path in alternative_paths:
        if os.path.exists(alt_path):
            return alt_path

    # Если файл не найден нигде
    logger.warning(f"Ресурс не найден: {relative_path}")
    return None


class SmartSearchLineEdit(QLineEdit):
    """Умное поле поиска с подсказками"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Поиск по названию...")

        # Настраиваем автодополнение
        self.completer = QCompleter([])
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setCompleter(self.completer)

        # Ищем иконку поиска
        icon_path = resource_path("../img/search_icon.png")

        # Добавляем иконку поиска
        self.search_icon = QLabel()
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(16, 16)
            self.search_icon.setPixmap(pixmap)
        else:
            # Используем текстовую иконку если файл не найден
            self.search_icon.setText("🔍")
            self.search_icon.setStyleSheet("font-size: 14px; color: #666;")

        self.search_icon.setStyleSheet("padding-left: 5px;")

        layout = QHBoxLayout(self)
        layout.addWidget(self.search_icon)
        layout.addStretch()
        layout.setContentsMargins(5, 0, 5, 0)

        # Добавляем отступ слева для текста
        self.setTextMargins(25, 0, 5, 0)

    def set_search_suggestions(self, suggestions):
        """Устанавливает список подсказок для автодополнения"""
        self.completer.setModel(QStringListModel(suggestions))


# ====================================================================================
# FlowLayout - кастомный layout для расположения виджетов как в веб-потоке
# ====================================================================================
class FlowLayout(QLayout):
    """ Располагает виджеты в потоке слева направо, с переносом на новую строку при нехватке места """

    def __init__(self, parent=None, margin=15, h_spacing=15, v_spacing=15):
        super().__init__(parent)

        # Установка отступов от краев контейнера
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self._h_spacing = h_spacing  # Горизонтальный отступ между виджетами
        self._v_spacing = v_spacing  # Вертикальный отступ между строками
        self._items = []  # Список для хранения элементов layout
        self._geometry_cache = None  # Кэш для геометрии (для оптимизации)

    def __del__(self):
        """Деструктор - очищает все элементы layout при удалении."""
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        """Добавляет элемент в layout и сбрасывает кэш геометрии."""
        self._items.append(item)
        self._geometry_cache = None  # Сброс кэша при добавлении нового элемента

    def horizontalSpacing(self):
        """Возвращает значение горизонтального отступа."""
        return self._h_spacing

    def verticalSpacing(self):
        """Возвращает значение вертикального отступа."""
        return self._v_spacing

    def count(self):
        """Возвращает количество элементов в layout."""
        return len(self._items)

    def itemAt(self, index):
        """Возвращает элемент по указанному индексу."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        """Удаляет и возвращает элемент по указанному индексу."""
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            self._geometry_cache = None  # Сброс кэша при удалении элемента
            return item
        return None

    def expandingDirections(self):
        """Определяет направления расширения layout (в данном случае не расширяется)."""
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        """Возвращает True, так как высота layout зависит от его ширины."""
        return True

    def heightForWidth(self, width):
        """Вычисляет необходимую высоту layout для заданной ширины."""
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        """Устанавливает геометрию layout и размещает в нем элементы."""
        super().setGeometry(rect)  # Вызов родительского метода
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        """Возвращает рекомендуемый размер layout."""
        return self.minimumSize()

    def minimumSize(self):
        """Вычисляет минимальный размер layout."""
        size = QSize()  # Создаем объект размера
        for item in self._items:
            size = size.expandedTo(item.minimumSize())

        # Добавляем отступы к размеру
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        """ Основной метод для расстановки элементов в layout.
        rect: Прямоугольная область для размещения
        test_only: Если True, только вычисляет высоту без фактического размещения
        """
        # Получаем реальную рабочую область с учетом отступов
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(+left, +top, -right, -bottom)  # Область внутри отступов
        x = effective_rect.x()  # Текущая позиция X
        y = effective_rect.y()  # Текущая позиция Y
        line_height = 0  # Высота текущей строки

        # Проходим по всем элементам layout
        for item in self._items:
            widget = item.widget()
            if widget is None:
                continue  # Пропускаем элементы без виджета

            space_x = self.horizontalSpacing()  # Горизонтальный отступ
            space_y = self.verticalSpacing()  # Вертикальный отступ

            # Вычисляем позицию для следующего элемента
            next_x = x + item.sizeHint().width() + space_x

            # Если следующий элемент не помещается в текущей строке
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()  # Переходим на новую строку
                y = y + line_height + space_y  # Увеличиваем Y на высоту строки + отступ
                next_x = x + item.sizeHint().width() + space_x  # Пересчитываем next_x
                line_height = 0  # Сбрасываем высоту строки

            # Если не тестовый режим, устанавливаем геометрию элемента
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x  # Обновляем текущую позицию X
            # Обновляем высоту строки (максимальная высота элементов в строке)
            line_height = max(line_height, item.sizeHint().height())

        # Возвращаем общую высоту layout
        return y + line_height - rect.y() + bottom

    def invalidate(self):
        """Сбрасывает кэш геометрии при изменении layout."""
        super().invalidate()
        self._geometry_cache = None


# ====================================================================================
# CartItemWidget - виджет элемента корзины с чекбоксом
# ====================================================================================
class CartItemWidget(QWidget):
    """Виджет для отображения элемента корзины с возможностью выбора чекбоксом."""

    def __init__(self, ingredient_name, quantity, unit, parent=None):
        super().__init__(parent)
        self.ingredient_name = ingredient_name  # Сохраняем название ингредиента
        self.quantity = quantity  # Сохраняем количество
        self.unit = unit  # Сохраняем единицу измерения
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса виджета."""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)  # Устанавливаем отступы внутри виджета

        # Создаем чекбокс для выбора элемента
        self.checkbox = QCheckBox()
        # Стили для чекбокса
        self.checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 8px;  /* Отступ между чекбоксом и текстом */
            }
            QCheckBox::indicator {
                width: 16px;   /* Ширина индикатора чекбокса */
                height: 16px;  /* Высота индикатора чекбокса */
            }
        """)

        # Форматируем количество для красивого отображения
        quantity_text = str(self.quantity)
        try:
            # Пытаемся преобразовать количество в число для форматирования
            quantity_float = float(self.quantity)
            if quantity_float == int(quantity_float):  # Если целое число
                quantity_text = str(int(quantity_float))
            else:  # Если дробное число
                quantity_text = f"{quantity_float:.2f}"  # Округляем до 2 знаков
        except ValueError:
            pass  # Оставляем как есть

        # Создаем метку для отображения информации об ингредиенте
        text_label = QLabel(f"{self.ingredient_name}: {quantity_text} {self.unit}")
        # Устанавливаем стили для метки
        text_label.setStyleSheet("""
            QLabel { 
                color: #2c3e50;       /* Темно-синий цвет текста */
                font-size: 14px;      /* Размер шрифта */
                padding: 5px;         /* Внутренние отступы */
            }
        """)

        # Добавляем виджеты в layout
        layout.addWidget(self.checkbox)  # Чекбокс слева
        layout.addWidget(text_label)  # Текст ингредиента
        layout.addStretch()  # Растягиваемое пространство справа

        self.setLayout(layout)  # Устанавливаем layout для виджета

    def is_checked(self):
        """Проверяет, отмечен ли чекбокс."""
        return self.checkbox.isChecked()


# ====================================================================================
# RecipeCard - виджет карточки рецепта для главного окна
# ====================================================================================
class RecipeCard(QFrame):
    """Виджет карточки рецепта"""

    def __init__(self, recipe_data, db, parent=None):
        """ Инициализация карточки рецепта. """
        super().__init__(parent)
        self.recipe_data = recipe_data  # Сохраняем данные рецепта
        self.db = db
        self.parent = parent  # Сохраняем родительский виджет
        self.user_id = parent.user_id if parent else None  # Получаем ID пользователя
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса карточки."""
        self.setFixedWidth(250)
        self.setMinimumHeight(280)
        self.setMaximumHeight(340)

        # Устанавливаем стили для карточки
        self.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 1px solid #dee2e6;
                        border-radius: 12px;
                        margin: 0px;
                        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
                        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                    }
                    QFrame:hover {
                        box-shadow: 0 8px 25px rgba(52, 152, 219, 0.15);
                        transform: translateY(-3px);
                    }
                    QFrame:pressed {
                        transform: translateY(-1px);
                    }
                """)

        # Создаем вертикальный layout для карточки
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Без внутренних отступов
        layout.setSpacing(0)  # Без отступов между элементами

        # === ВЕРХНЯЯ ЧАСТЬ: Изображение рецепта ===
        image_container = QWidget()
        image_container.setFixedHeight(150)
        # Устанавливаем стили для контейнера изображения с градиентом
        image_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,  /* Вертикальный градиент */
                    stop:0 #f8f9fa, stop:1 #e9ecef);                /* От светлого к более темному серому */
                border-top-left-radius: 12px;                        /* Закругление верхних углов */
                border-top-right-radius: 12px;                       /* Закругление верхних углов */
                border-bottom: 1px solid #e9ecef;                    /* Нижняя граница */
            }
        """)

        # Создаем layout для изображения
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Выравнивание по центру

        # Загружаем изображение рецепта из бд
        pixmap = self.db.get_recipe_image(self.recipe_data[0])
        if pixmap and not pixmap.isNull():  # Если изображение успешно загружено
            # Масштабируем изображение с сохранением пропорций
            scaled_pixmap = pixmap.scaled(248, 148, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                          Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)  # Устанавливаем изображение
            self.image_label.setScaledContents(True)  # Включаем масштабирование содержимого
        else:  # Если изображение не загружено
            # Создаем текстовую заглушку с названием рецепта
            recipe_name = self.recipe_data[2]
            if len(recipe_name) > 22:  # Если название слишком длинное
                display_text = recipe_name[:22] + '...'  # Обрезаем и добавляем многоточие
            else:
                display_text = recipe_name

            # Устанавливаем стили для текстовой заглушки
            self.image_label.setText(f"🍳\n{display_text}")
            self.image_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;          /* Серый цвет текста */
                    font-size: 14px;         /* Размер шрифта */
                    font-weight: 500;        /* Средняя жирность */
                    padding: 20px;           /* Внутренние отступы */
                    line-height: 1.4;        /* Межстрочный интервал */
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,  /* Градиентный фон */
                        stop:0 #e3f2fd, stop:1 #bbdefb);                /* От голубого к светло-голубому */
                }
            """)
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_layout.addWidget(self.image_label)  # Добавляем метку изображения в layout
        layout.addWidget(image_container)  # Добавляем контейнер изображения в основной layout

        # === ЦЕНТРАЛЬНАЯ ЧАСТЬ: Основная информация ===
        info_container = QWidget()
        info_container.setStyleSheet("background-color: white;")
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(10)

        # Название рецепта
        name_label = QLabel(self.recipe_data[2])
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Выравнивание по левому краю
        # Устанавливаем стили для названия
        name_label.setStyleSheet("""
            QLabel {
                font-weight: 600;            /* Полужирный шрифт */
                font-size: 16px;             /* Размер шрифта */
                color: #2c3e50;              /* Темно-синий цвет */
                line-height: 1.3;            /* Межстрочный интервал */
                padding-bottom: 5px;         /* Нижний отступ */
                border-bottom: 1px solid #f1f3f4;  /* Нижняя граница */
            }
        """)
        name_label.setWordWrap(True)  # Включение переноса слов
        name_label.setMinimumHeight(45)
        name_label.setMaximumHeight(60)
        info_layout.addWidget(name_label)

        # === БЛОК МЕТА-ИНФОРМАЦИИ ===
        meta_container = QWidget()
        meta_container.setStyleSheet("background-color: white;")
        meta_layout = QVBoxLayout(meta_container)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(8)

        # Информационная строка (кухня и время)
        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 0, 0, 0)
        info_row.setSpacing(10)

        # Кухня
        cuisine = self.recipe_data[17] if len(self.recipe_data) > 17 else None
        if cuisine:
            cuisine_widget = QWidget()
            cuisine_widget.setFixedHeight(24)
            cuisine_widget.setStyleSheet("""
                        QWidget {
                            background-color: #e8f5e9;
                            border-radius: 4px;
                            border: 1px solid #c8e6c9;
                        }
                    """)

            cuisine_layout = QHBoxLayout(cuisine_widget)
            cuisine_layout.setContentsMargins(6, 2, 6, 2)
            cuisine_label = QLabel(f"🌍 {cuisine[:12]}" if len(cuisine) > 12 else f"🌍 {cuisine}")
            cuisine_label.setStyleSheet("font-size: 10px; font-weight: 500; color: #2e7d32;")
            cuisine_label.setToolTip(f"Кухня: {cuisine}")
            cuisine_layout.addWidget(cuisine_label)
            info_row.addWidget(cuisine_widget)

        # Время приготовления
        time_widget = QWidget()
        time_widget.setFixedHeight(24)
        time_widget.setStyleSheet("""
                    QWidget {
                        background-color: #e3f2fd;
                        border-radius: 4px;
                        border: 1px solid #bbdefb;
                    }
                """)

        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(6, 2, 6, 2)
        time_label = QLabel(f"⏱{self.recipe_data[8] or '?'}м")
        time_label.setStyleSheet("font-size: 10px; font-weight: 500; color: #1976d2;")
        time_layout.addWidget(time_label)
        info_row.addWidget(time_widget)

        info_row.addStretch()
        meta_layout.addLayout(info_row)

        # === БЛОК СТАТУСОВ ===
        status_container = QWidget()
        status_container.setFixedHeight(90)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)  # Отступы между кнопками

        # Кнопка "Избранное"
        self.is_favorite = self.recipe_data[15] if len(self.recipe_data) > 15 else False
        self.favorite_btn = QPushButton("❤️" if self.is_favorite else "🤍")
        self.favorite_btn.setFixedSize(50, 50)  # Фиксированный размер кнопки
        # Стили для кнопки избранного
        self.favorite_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;      /* Прозрачный фон */
                border: none;                       /* Без рамки */
                border-radius: 2px;                /* Круглая кнопка */
                font-size: 17px;                    /* Размер шрифта */
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 0.1);  /* Красный фон при наведении */
                transform: scale(1.1);                     /* Увеличение при наведении */
            }
        """)
        # Подсказка в зависимости от состояния
        self.favorite_btn.setToolTip("В избранном" if self.is_favorite else "Добавить в избранное")
        self.favorite_btn.clicked.connect(self.toggle_favorite_status)  # Подключаем обработчик

        # Кнопка "Приготовлено"
        self.is_cooked = self.recipe_data[16] if len(self.recipe_data) > 16 else False
        self.cooked_btn = QPushButton("✅" if self.is_cooked else "⏳")
        self.cooked_btn.setFixedSize(50, 50)  # Фиксированный размер кнопки
        # Стили для кнопки приготовленного
        self.cooked_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;      /* Прозрачный фон */
                border: none;                       /* Без рамки */
                border-radius: 2px;                /* Круглая кнопка */
                font-size: 18px;                    /* Размер шрифта */
            }
            QPushButton:hover {
                background-color: rgba(40, 167, 69, 0.1);  /* Зеленый фон при наведении */
                transform: scale(1.1);                     /* Увеличение при наведении */
            }
        """)
        # Подсказка в зависимости от состояния
        self.cooked_btn.setToolTip("Приготовлено" if self.is_cooked else "Отметить как приготовленное")
        self.cooked_btn.clicked.connect(self.toggle_cooked_status)

        # Добавляем тип блюда
        dish_type = self.recipe_data[18] if len(self.recipe_data) > 18 else "Без категории"
        dish_type_widget = QWidget()
        dish_type_widget.setFixedHeight(24)
        dish_type_widget.setStyleSheet("""
                    QWidget {
                        background-color: #f3e5f5;
                        border-radius: 4px;
                        border: 1px solid #e1bee7;
                    }
                """)

        dish_type_layout = QHBoxLayout(dish_type_widget)
        dish_type_layout.setContentsMargins(6, 2, 6, 2)

        # Определяем иконку в зависимости от типа блюда
        type_icons = {
            "Салаты": "🥗",
            "Десерты": "🍰",
            "Основные блюда": "🍛",
            "Завтраки": "🍳",
            "Гарниры": "🥔",
            "Супы": "🍲"
        }
        icon = type_icons.get(dish_type, "🍽️")

        dish_type_label = QLabel(f"{icon} {dish_type[:12]}" if len(dish_type) > 12 else f"{icon} {dish_type}")
        dish_type_label.setStyleSheet("font-size: 10px; font-weight: 500; color: #7b1fa2;")
        dish_type_label.setToolTip(f"Тип блюда: {dish_type}")
        dish_type_layout.addWidget(dish_type_label)

        status_layout.addWidget(self.favorite_btn)  # Добавляем кнопку избранного
        status_layout.addWidget(self.cooked_btn)  # Добавляем кнопку приготовленного
        status_layout.addWidget(dish_type_widget)
        status_layout.addStretch()

        meta_layout.addWidget(status_container)  # Добавляем контейнер с кнопками в meta layout
        info_layout.addWidget(meta_container)  # Добавляем мета-информацию в info layout

        layout.addWidget(info_container)  # Добавляем info container в основной layout

        # === ОСНОВАНИЕ КАРТОЧКИ: Цветная полоска ===
        bottom_line = QWidget()
        bottom_line.setFixedHeight(4)  # Фиксированная высота
        # Градиентная полоска внизу карточки
        bottom_line.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,  /* Горизонтальный градиент */
                    stop:0 #3498db, stop:1 #2ecc71);                /* От синего к зеленому */
                border-bottom-left-radius: 12px;                     /* Закругление нижних углов */
                border-bottom-right-radius: 12px;                    /* Закругление нижних углов */
            }
        """)
        layout.addWidget(bottom_line)  # Добавляем полоску в layout

        self.setLayout(layout)  # Устанавливаем основной layout для карточки

    def toggle_favorite_status(self):
        """Переключает статус избранного для рецепта."""
        try:
            if self.user_id:
                new_status = not self.is_favorite  # Инвертируем текущий статус
                success = self.db.toggle_favorite(self.user_id, self.recipe_data[0])

                if success:
                    self.is_favorite = new_status  # Обновляем локальный статус
                    # Обновляем иконку кнопки
                    self.favorite_btn.setText("❤️" if new_status else "🤍")
                    # Обновляем подсказку
                    self.favorite_btn.setToolTip("В избранном" if new_status else "Добавить в избранное")

                    # Обновляем данные в recipe_data для синхронизации
                    if len(self.recipe_data) > 15:
                        self.recipe_data = list(self.recipe_data)
                        self.recipe_data[15] = new_status
                        self.recipe_data = tuple(self.recipe_data)

                    # Обновляем статистику в профиле
                    if self.parent:
                        self.parent.update_profile()

        except Exception as e:
            logger.error(f"Ошибка при переключении статуса избранного: {e}")

    def toggle_cooked_status(self):
        """Переключает статус приготовленного для рецепта."""
        try:
            if self.user_id:
                new_status = not self.is_cooked  # Инвертируем текущий статус
                success = self.db.mark_recipe_as_cooked(self.user_id, self.recipe_data[0], new_status)

                if success:
                    self.is_cooked = new_status  # Обновляем локальный статус
                    # Обновляем иконку кнопки
                    self.cooked_btn.setText("✅" if new_status else "⏳")
                    # Обновляем подсказку
                    self.cooked_btn.setToolTip("Приготовлено" if new_status else "Отметить как приготовленное")

                    # Обновляем данные в recipe_data для синхронизации
                    if len(self.recipe_data) > 16:
                        self.recipe_data = list(self.recipe_data)
                        self.recipe_data[16] = new_status
                        self.recipe_data = tuple(self.recipe_data)

                    # Обновляем статистику в профиле
                    if self.parent:
                        self.parent.update_profile()

        except Exception as e:
            logger.error(f"Ошибка при переключении статуса приготовления: {e}")

    def mouseDoubleClickEvent(self, event):
        """Обработчик двойного клика по карточке - открывает диалог просмотра рецепта."""
        self.parent.view_recipe(self.recipe_data)


# ====================================================================================
# ProfileRecipeCard - карточка рецепта для профиля пользователя
# ====================================================================================
class ProfileRecipeCard(QFrame):
    """Виджет карточки рецепта для отображения в профиле пользователя."""

    def __init__(self, recipe_data, db, parent=None):
        """ Инициализация карточки рецепта для профиля. """
        super().__init__(parent)
        self.recipe_data = recipe_data
        self.db = db
        self.parent = parent
        self.user_id = parent.user_id if parent else None
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса карточки профиля."""
        self.setFixedSize(180, 220)
        # Устанавливаем стили для карточки с тенями
        self.setStyleSheet("""
            QFrame {
                background-color: white;                    /* Белый фон */
                border: none;                               /* Без рамки */
                border-radius: 10px;                        /* Закругленные углы */
                margin: 5px;                                /* Внешние отступы */
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); /* Легкая тень */
                transition: all 0.2s ease;                  /* Плавный переход */
            }
            QFrame:hover {
                box-shadow: 0 4px 15px rgba(52, 152, 219, 0.12);  /* Усиленная тень при наведении */
                transform: translateY(-2px);                /* Легкий подъем при наведении */
            }
        """)

        # Создаем вертикальный layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Контейнер для изображения
        image_container = QWidget()
        image_container.setFixedHeight(120)
        # Стили для контейнера изображения с градиентом
        image_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,  /* Вертикальный градиент */
                    stop:0 #f5f7fa, stop:1 #e4e7eb);                /* От светлого к темному серому */
                border-top-left-radius: 10px;                        /* Закругление верхних углов */
                border-top-right-radius: 10px;                       /* Закругление верхних углов */
                border-bottom: 1px solid #e9ecef;                    /* Нижняя граница */
            }
        """)

        # Layout для изображения
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Загружаем изображение рецепта
        pixmap = self.db.get_recipe_image(self.recipe_data[0])
        if pixmap and not pixmap.isNull():  # Если изображение загружено
            # Масштабируем изображение
            scaled_pixmap = pixmap.scaled(178, 118, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                          Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)  # Устанавливаем изображение
            image_label.setScaledContents(True)  # Включаем масштабирование
        else:  # Если изображение не загружено
            image_label.setText("🍳")  # Текстовая иконка
            image_label.setStyleSheet("font-size: 32px; color: #6c757d;")  # Стили для иконки

        image_layout.addWidget(image_label)
        layout.addWidget(image_container)

        # Контейнер для информации
        info_container = QWidget()
        info_container.setStyleSheet("background-color: white;")
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(12, 12, 12, 12)
        info_layout.setSpacing(8)

        # Название рецепта
        name_label = QLabel(self.recipe_data[2])
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Стили для названия
        name_label.setStyleSheet("""
            QLabel {
                font-size: 12px;             /* Размер шрифта */
                font-weight: 500;            /* Средняя жирность */
                color: #2c3e50;              /* Темно-синий цвет */
                line-height: 1.3;            /* Межстрочный интервал */
            }
        """)
        name_label.setWordWrap(True)  # Включение переноса слов
        name_label.setMaximumHeight(40)
        info_layout.addWidget(name_label)

        # Контейнер для статусов (избранное/приготовлено)
        status_container = QWidget()
        status_container.setFixedHeight(20)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(5)

        # Проверяем статусы рецепта
        is_cooked = len(self.recipe_data) > 16 and self.recipe_data[16]
        is_favorite = self.recipe_data[15] if len(self.recipe_data) > 15 else False

        if is_cooked:  # Если рецепт приготовлен
            cooked_icon = QLabel("✅")
            cooked_icon.setStyleSheet("font-size: 10px;")
            status_layout.addWidget(cooked_icon)

        if is_favorite:  # Если рецепт в избранном
            favorite_icon = QLabel("❤️")
            favorite_icon.setStyleSheet("font-size: 10px;")
            status_layout.addWidget(favorite_icon)

        status_layout.addStretch()  # Растягиваемое пространство
        info_layout.addWidget(status_container)

        layout.addWidget(info_container)

        self.setLayout(layout)

    def mouseDoubleClickEvent(self, event):
        """Обработчик двойного клика по карточке - открывает диалог просмотра рецепта."""
        self.parent.view_recipe(self.recipe_data)


class AutoCompleteComboBox(QComboBox):
    """ComboBox с автодополнением и возможностью ввода нескольких значений"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.completer = self.completer()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        # Разрешаем ввод нескольких значений через запятую
        self.lineEdit().textChanged.connect(self.on_text_changed)

    def on_text_changed(self, text):
        """Обрабатывает изменение текста для автодополнения"""
        if ',' in text:
            # Если введена запятая, оставляем только последнюю часть для автодополнения
            last_part = text.split(',')[-1].strip()
            if last_part:
                self.completer.setCompletionPrefix(last_part)
                if self.completer.completionCount() > 0:
                    self.completer.complete()

    def text(self):
        """Возвращает текущий текст комбобокса"""
        return self.currentText()


# ====================================================================================
# MainWindow - главное окно приложения
# ====================================================================================
class MainWindow(QMainWindow):
    """Главное окно приложения с вкладками рецептов, профиля и корзины."""

    def __init__(self, db, user_id, logout_callback):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.logout_callback = logout_callback

        self.settings = QSettings("PuzzleVkusov", "AppSettings")
        self.cart = self.db.get_cart_items(user_id)
        self.current_recipe_cards = []

        # Таймер для отложенной фильтрации
        self.filter_timer = QTimer()
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.load_recipes)

        self.init_ui()
        self.load_initial_settings()
        self.load_recipes()
        self.update_profile()
        self.update_cart_display()

    def init_ui(self):
        """Инициализация пользовательского интерфейса главного окна."""
        self.setWindowTitle("Пазл Вкусов")
        self.setGeometry(100, 100, 1200, 850)
        self.setWindowIcon(QIcon(resource_path("img/icon.ico")))

        # Загружаем настройки шрифтов
        font_size = self.settings.value("font_size", 14, type=int)
        title_font_size = self.settings.value("title_font_size", 16, type=int)

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f8f9fa;
            }}
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {font_size}px;
            }}
            /* Стили для полей поиска */
            QLineEdit {{
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border: 1px solid #007bff;
                outline: none;
            }}
            QComboBox {{
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }}
            QComboBox:focus {{
                border: 1px solid #007bff;
                outline: none;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #007bff;
                selection-color: white;
            }}
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {font_size}px;
            }}
            QTabWidget::pane {{
                border: 1px solid #dee2e6;
                background-color: white;
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: #e9ecef;
                color: #495057;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: {font_size}px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: #495057;
                border-bottom: 2px solid #007bff;
            }}
            QPushButton {{
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
        """)

        self.setMenuBar(None)
        self.create_toolbar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        self.tabs = QTabWidget()

        # === ВКЛАДКА РЕЦЕПТОВ ===
        recipes_tab = QWidget()
        recipes_layout = QVBoxLayout(recipes_tab)
        recipes_layout.setContentsMargins(0, 0, 0, 0)
        recipes_layout.setSpacing(10)

        self.setup_recipe_filters(recipes_layout)

        # Панель управления рецептами
        recipes_control_layout = QHBoxLayout()
        add_recipe_btn = QPushButton("➕ Добавить рецепт")
        add_recipe_btn.clicked.connect(self.add_recipe)
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.load_recipes)

        # Кнопка принудительного обновления БД
        force_refresh_btn = QPushButton("🔧 Исправить БД")
        force_refresh_btn.clicked.connect(self.fix_database)
        force_refresh_btn.setStyleSheet("background-color: #ffc107;")

        recipes_control_layout.addWidget(add_recipe_btn)
        recipes_control_layout.addWidget(refresh_btn)
        recipes_control_layout.addStretch()
        recipes_layout.addLayout(recipes_control_layout)

        # Область прокрутки для рецептов
        self.recipes_scroll = QScrollArea()
        self.recipes_scroll.setWidgetResizable(True)
        self.recipes_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # убираем горизонтальную прокрутку
        self.recipes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Главный контейнер для всех рецептов
        self.recipes_container = QWidget()
        self.recipes_container_layout = QVBoxLayout(self.recipes_container)
        self.recipes_container_layout.setSpacing(20)
        self.recipes_container_layout.setContentsMargins(10, 10, 10, 10)
        self.recipes_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравнивание по верху

        self.recipes_scroll.setWidget(self.recipes_container)

        # Устанавливаем стили для скролла
        self.recipes_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f3f4;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
        """)

        recipes_layout.addWidget(self.recipes_scroll, 1)  # 1 для растяжения

        # === ВКЛАДКА ПРОФИЛЯ ===
        profile_tab = QWidget()
        profile_layout = QVBoxLayout()
        self.setup_profile_tab(profile_layout)
        profile_tab.setLayout(profile_layout)

        # === ВКЛАДКА КОРЗИНЫ ===
        cart_tab = QWidget()
        cart_layout = QVBoxLayout()
        self.setup_cart_tab(cart_layout)
        cart_tab.setLayout(cart_layout)

        self.tabs.addTab(recipes_tab, "📖 Рецепты")
        self.tabs.addTab(profile_tab, "👤 Профиль")
        self.tabs.addTab(cart_tab, "🛒 Корзина")

        layout.addWidget(self.tabs, 1)  # Tabs тоже растягиваются
        central_widget.setLayout(layout)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готово", 3000)  # Показываем начальное сообщение на 3 секунды

    def fix_database(self):
        """Исправление проблем с базой данных"""
        try:
            reply = QMessageBox.question(
                self,
                "Исправление БД",
                "Принудительно пересоздаст изображения и проверит рецепты.\nПродолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Принудительно назначаем изображения
                self.db.assign_unique_images_to_recipes()

                # Проверяем статус
                self.db.check_image_status()

                # Обновляем отображение
                self.load_recipes()
                self.update_profile()

                QMessageBox.information(self, "Готово", "База данных исправлена!")

        except Exception as e:
            logger.error(f"Ошибка при исправлении БД: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")

    def load_initial_settings(self):
        """Загружает начальные настройки приложения при запуске."""
        try:
            # Загружаем размер шрифта из настроек (по умолчанию 14)
            font_size = self.settings.value("font_size", 14, type=int)
            # Загружаем размер шрифта заголовков (по умолчанию 16)
            title_font_size = self.settings.value("title_font_size", 16, type=int)
            self.update_styles(font_size, title_font_size)  # Применяем стили
        except Exception as e:
            logger.error(f"Ошибка загрузки начальных настроек: {e}")

    def create_toolbar(self):
        """Создает панель инструментов с иконками в верхней части окна."""
        # Создаем панель инструментов
        toolbar = QToolBar("Главное меню")
        toolbar.setMovable(False)  # Запрещаем перетаскивание панели
        # Устанавливаем стили для панели инструментов
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;          /* Светло-серый фон */
                border-bottom: 1px solid #dee2e6;   /* Нижняя граница */
                spacing: 5px;                       /* Отступы между элементами */
                padding: 5px;                       /* Внутренние отступы */
            }
            QToolButton {
                padding: 5px;                       /* Внутренние отступы кнопок */
                border-radius: 4px;                 /* Закругленные углы */
                background-color: transparent;      /* Прозрачный фон */
            }
            QToolButton:hover {
                background-color: #e9ecef;          /* Светло-серый фон при наведении */
            }
        """)

        # Функция для создания действий с иконками
        def create_action(icon_name, fallback_text, tooltip, callback):
            """Создает действие с иконкой или текстовой заменой."""
            icon_path = resource_path(f"img/{icon_name}")
            if icon_path and os.path.exists(icon_path):
                action = QAction(QIcon(icon_path), "", self)
            else:
                action = QAction(fallback_text, self)
                logger.warning(f"Иконка {icon_name} не найдена")

            action.triggered.connect(callback)
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)
            return action

        # Создаем действие для кнопки "Настройки"
        settings_action = create_action("settings_icon.png", "⚙️", "Настройки приложения", self.open_settings)
        help_action = create_action("help_icon.png", "❓", "Справка", self.open_help)
        refresh_action = create_action("refresh_icon.png", "🔄", "Обновить данные", self.refresh_data)

        # Добавляем действия на панель инструментов
        toolbar.addAction(settings_action)
        toolbar.addAction(help_action)
        toolbar.addAction(refresh_action)

        # Добавляем панель инструментов в главное окно
        self.addToolBar(toolbar)
        toolbar.setIconSize(QSize(24, 24))

    def setup_profile_tab(self, layout):
        """Настраивает содержимое вкладки профиля пользователя."""

        # Простое поле с информацией о пользователе
        self.profile_info = QLabel()
        # Устанавливаем стили для информации профиля
        self.profile_info.setStyleSheet("""
            QLabel {
                font-size: 16px;           /* Размер шрифта */
                color: #495057;            /* Темно-серый цвет */
                background-color: white;   /* Белый фон */
                padding: 15px;             /* Внутренние отступы */
                border-radius: 8px;        /* Закругленные углы */
                border: 1px solid #dee2e6; /* Серая рамка */
                min-height: 60px;          /* Минимальная высота */
            }
        """)
        self.profile_info.setWordWrap(True)  # Включение переноса слов

        layout.addWidget(self.profile_info)  # Добавляем виджет

        # Статистика
        stats_group = QLabel("📊 Статистика")
        stats_group.setStyleSheet("""
            font-size: 16px;           /* Размер шрифта */
            font-weight: bold;         /* Жирный шрифт */
            color: #2c3e50;            /* Темно-синий цвет */
            margin-top: 20px;          /* Верхний отступ */
        """)
        layout.addWidget(stats_group)

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                font-size: 14px;           /* Размер шрифта */
                color: #495057;            /* Темно-серый цвет */
                background-color: white;   /* Белый фон */
                padding: 20px;             /* Внутренние отступы */
                border-radius: 8px;        /* Закругленные углы */
                border: 1px solid #dee2e6; /* Серая рамка */
                min-height: 120px;         /* Минимальная высота */
            }
        """)
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)

        # Избранные рецепты
        favorites_label = QLabel("❤️ Избранные рецепты")
        favorites_label.setStyleSheet("""
            font-size: 16px;                
            font-weight: 600;               
            color: #2c3e50;                 
            margin-top: 20px;                
            padding-bottom: 8px;             
            border-bottom: 2px solid #e9ecef; 
        """)
        layout.addWidget(favorites_label)

        self.favorites_scroll = QScrollArea()
        self.favorites_widget = QWidget()
        self.favorites_layout = QHBoxLayout(self.favorites_widget)
        self.favorites_layout.setSpacing(10)
        self.favorites_layout.setContentsMargins(15, 10, 15, 10)
        self.favorites_layout.addStretch(1)

        self.favorites_scroll.setWidget(self.favorites_widget)
        self.favorites_scroll.setWidgetResizable(True)
        self.favorites_scroll.setFixedHeight(270)
        self.favorites_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        layout.addWidget(self.favorites_scroll)

        # Приготовленные рецепты
        cooked_label = QLabel("✅ Приготовленные рецепты")
        cooked_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 20px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
        """)
        layout.addWidget(cooked_label)

        self.cooked_scroll = QScrollArea()
        self.cooked_widget = QWidget()
        self.cooked_layout = QHBoxLayout(self.cooked_widget)
        self.cooked_layout.setSpacing(10)
        self.cooked_layout.setContentsMargins(15, 10, 15, 10)
        self.cooked_layout.addStretch(1)

        self.cooked_scroll.setWidget(self.cooked_widget)
        self.cooked_scroll.setWidgetResizable(True)
        self.cooked_scroll.setFixedHeight(270)
        self.cooked_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        layout.addWidget(self.cooked_scroll)

        # Кнопка выхода
        logout_layout = QHBoxLayout()
        logout_btn = QPushButton("🚪 Выйти из аккаунта")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        logout_layout.addWidget(logout_btn)
        logout_layout.addStretch()
        layout.addLayout(logout_layout)

    def setup_recipe_filters(self, layout):
        """Настраивает панель фильтрации рецептов с чекбоксами для ингредиентов"""
        filters_container = QWidget()
        filters_container.setFixedHeight(150)  # Увеличиваем высоту
        filters_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)

        filters_layout = QVBoxLayout(filters_container)
        filters_layout.setContentsMargins(15, 10, 15, 10)

        # Первая строка фильтров (основные)
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)

        # Кухня
        row1_layout.addWidget(QLabel("Кухня:"))
        self.cuisine_filter = QComboBox()
        self.cuisine_filter.setMinimumWidth(150)
        self.cuisine_filter.addItem("Любая кухня")
        self.load_cuisines_to_filter()
        self.cuisine_filter.currentTextChanged.connect(lambda: self.apply_filters(immediate=True))
        row1_layout.addWidget(self.cuisine_filter)

        # Время приготовления
        row1_layout.addWidget(QLabel("Время:"))
        self.time_filter = QComboBox()
        self.time_filter.setMinimumWidth(120)
        self.time_filter.addItems(["Любое", "15 мин", "30 мин", "60 мин", "90 мин", "120 мин"])
        self.time_filter.currentTextChanged.connect(lambda: self.apply_filters(immediate=True))
        row1_layout.addWidget(self.time_filter)

        # Чекбоксы
        self.favorites_only = QCheckBox("Только избранное")
        self.favorites_only.stateChanged.connect(lambda: self.apply_filters(immediate=True))
        row1_layout.addWidget(self.favorites_only)

        self.cooked_only = QCheckBox("Только приготовленные")
        self.cooked_only.stateChanged.connect(lambda: self.apply_filters(immediate=True))
        row1_layout.addWidget(self.cooked_only)

        row1_layout.addStretch()
        filters_layout.addLayout(row1_layout)

        # Вторая строка фильтров (поиск)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(10)

        # Поиск по названию рецепта
        row2_layout.addWidget(QLabel("Название:"))
        self.name_filter = SmartSearchLineEdit()
        self.name_filter.setMinimumWidth(250)
        self.name_filter.textChanged.connect(lambda: self.apply_filters(debounced=True))
        self.load_search_suggestions()

        # Кнопка очистки для названия
        clear_name_btn = QPushButton("🗑️")
        clear_name_btn.setFixedSize(50, 40)
        clear_name_btn.setToolTip("Очистить поле названия")
        clear_name_btn.clicked.connect(self.clear_name_filter)

        row2_layout.addWidget(self.name_filter)
        row2_layout.addWidget(clear_name_btn)
        row2_layout.addStretch()

        filters_layout.addLayout(row2_layout)

        # Третья строка - фильтр по ингредиентам с чекбоксами
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(10)

        row3_layout.addWidget(QLabel("Ингредиенты:"))

        # Создаем виджет для чекбоксов ингредиентов
        self.ingredients_filter_container = QWidget()
        self.ingredients_filter_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #dee2e6;
                padding: 5px;
            }
        """)

        # Горизонтальный layout для чекбоксов
        self.ingredients_checkbox_layout = QHBoxLayout(self.ingredients_filter_container)
        self.ingredients_checkbox_layout.setSpacing(10)
        self.ingredients_checkbox_layout.setContentsMargins(5, 5, 5, 5)

        # Кнопка открытия списка ингредиентов
        self.ingredient_filter_btn = QPushButton("📋 Выбрать ингредиенты")
        self.ingredient_filter_btn.clicked.connect(self.show_ingredients_selection)
        self.ingredient_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)

        # Кнопка очистки выбора ингредиентов
        clear_ingredients_btn = QPushButton("🗑️")
        clear_ingredients_btn.setFixedSize(50, 40)
        clear_ingredients_btn.setToolTip("Очистить выбор ингредиентов")
        clear_ingredients_btn.clicked.connect(self.clear_ingredients_filter)

        row3_layout.addWidget(self.ingredient_filter_btn)
        row3_layout.addWidget(self.ingredients_filter_container, 1)  # Растягиваем
        row3_layout.addWidget(clear_ingredients_btn)

        filters_layout.addLayout(row3_layout)

        layout.addWidget(filters_container)

    def show_ingredients_selection(self):
        """Показывает диалог выбора ингредиентов"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор ингредиентов для фильтрации")
        dialog.setModal(True)
        dialog.resize(500, 600)

        layout = QVBoxLayout(dialog)

        # Поле поиска ингредиентов
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Поиск ингредиентов...")
        search_layout.addWidget(search_input)

        # Область с чекбоксами
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.ingredients_list_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        # Загружаем ингредиенты
        self.load_ingredients_for_checkboxes()

        # Кнопки
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Выбрать все")
        select_all_btn.clicked.connect(self.select_all_ingredients)
        clear_all_btn = QPushButton("Снять все")
        clear_all_btn.clicked.connect(self.clear_all_ingredients)
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(lambda: self.apply_ingredients_filter(dialog))
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(clear_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(search_layout)
        layout.addWidget(scroll_area)
        layout.addLayout(button_layout)

        dialog.exec()

    def load_ingredients_for_checkboxes(self):
        """Загружает ингредиенты для чекбоксов"""
        try:
            # Очищаем layout
            while self.ingredients_list_layout.count():
                item = self.ingredients_list_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Получаем ингредиенты
            ingredients = self.db.get_ingredients()

            # Сортируем по алфавиту
            ingredients.sort(key=lambda x: x[1].lower())

            # Создаем чекбоксы
            self.ingredient_checkboxes = {}
            for ing_id, ing_name in ingredients:
                checkbox = QCheckBox(ing_name)
                checkbox.setObjectName(f"ing_{ing_id}")
                self.ingredients_list_layout.addWidget(checkbox)
                self.ingredient_checkboxes[ing_name] = checkbox

            # Добавляем растягивающийся элемент
            self.ingredients_list_layout.addStretch()

        except Exception as e:
            logger.error(f"Ошибка загрузки ингредиентов для чекбоксов: {e}")

    def select_all_ingredients(self):
        """Выбирает все ингредиенты"""
        for checkbox in self.ingredient_checkboxes.values():
            checkbox.setChecked(True)

    def clear_all_ingredients(self):
        """Снимает выбор со всех ингредиентов"""
        for checkbox in self.ingredient_checkboxes.values():
            checkbox.setChecked(False)

    def apply_ingredients_filter(self, dialog):
        """Применяет выбранные ингредиенты"""
        selected_ingredients = []

        # Собираем выбранные ингредиенты
        for ing_name, checkbox in self.ingredient_checkboxes.items():
            if checkbox.isChecked():
                selected_ingredients.append(ing_name)

        # Обновляем отображение выбранных ингредиентов
        self.update_selected_ingredients_display(selected_ingredients)

        dialog.accept()
        self.load_recipes()

    def update_selected_ingredients_display(self, selected_ingredients):
        """Обновляет отображение выбранных ингредиентов"""
        # Очищаем контейнер
        while self.ingredients_checkbox_layout.count():
            item = self.ingredients_checkbox_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Добавляем выбранные ингредиенты в виде маленьких виджетов
        for i, ingredient in enumerate(selected_ingredients[:5]):  # Показываем до 5
            label = QLabel(f"• {ingredient}")
            label.setStyleSheet("""
                QLabel {
                    background-color: #e9ecef;
                    border-radius: 12px;
                    padding: 3px 8px;
                    font-size: 11px;
                    color: #495057;
                    margin-right: 5px;
                }
            """)
            self.ingredients_checkbox_layout.addWidget(label)

        # Если больше 5, показываем многоточие
        if len(selected_ingredients) > 5:
            label = QLabel(f"... ещё {len(selected_ingredients) - 5}")
            label.setStyleSheet("""
                QLabel {
                    background-color: #e9ecef;
                    border-radius: 12px;
                    padding: 3px 8px;
                    font-size: 11px;
                    color: #6c757d;
                    margin-right: 5px;
                }
            """)
            self.ingredients_checkbox_layout.addWidget(label)

        # Сохраняем выбранные ингредиенты
        self.selected_ingredients = selected_ingredients

        # Обновляем текст кнопки
        if selected_ingredients:
            self.ingredient_filter_btn.setText(f"📋 Выбрано: {len(selected_ingredients)}")
        else:
            self.ingredient_filter_btn.setText("📋 Выбрать ингредиенты")

    def load_search_suggestions(self):
        """Загружает подсказки для поиска по названиям рецептов"""
        try:
            # Получаем все рецепты для подсказок
            session = self.db.Session()
            recipes = session.query(Recipe).all()
            recipe_names = [recipe.name for recipe in recipes]
            session.close()

            # Устанавливаем подсказки
            self.name_filter.set_search_suggestions(recipe_names)

            logger.info(f"Загружено {len(recipe_names)} подсказок для поиска")

        except Exception as e:
            logger.error(f"Ошибка загрузки подсказок для поиска: {e}")

    def load_cuisines_to_filter(self):
        """Загружает список кухонь в фильтр"""
        try:
            cuisines = self.db.get_cuisines()
            logger.info(f"Загружено кухонь из базы: {len(cuisines)}")

            self.cuisine_filter.clear()
            self.cuisine_filter.addItem("Любая кухня")

            if cuisines:
                for cuisine_id, cuisine_name in cuisines:
                    self.cuisine_filter.addItem(cuisine_name)
            else:
                default_cuisines = ["Русская", "Итальянская", "Японская",
                                    "Китайская", "Мексиканская", "Французская"]
                for cuisine in default_cuisines:
                    self.cuisine_filter.addItem(cuisine)

        except Exception as e:
            logger.error(f"Ошибка загрузки кухонь: {e}")

    def clear_ingredients_filter(self):
        """Очищает выбор ингредиентов"""
        self.selected_ingredients = []
        self.update_selected_ingredients_display([])
        self.load_recipes()

    def clear_name_filter(self):
        """Очищает поле фильтра по названию"""
        self.name_filter.clear()
        self.load_recipes()

    def apply_filters(self, immediate=False, debounced=False):
        """Применяет фильтры"""
        if debounced:
            if hasattr(self, 'filter_timer'):
                self.filter_timer.stop()
                self.filter_timer.start(500)
        else:
            self.load_recipes()

    def reset_filters(self):
        """Сбрасывает все фильтры"""
        self.cuisine_filter.setCurrentIndex(0)
        self.time_filter.setCurrentIndex(0)
        self.favorites_only.setChecked(False)
        self.cooked_only.setChecked(False)
        self.ingredient_filter.lineEdit().clear()
        self.name_filter.clear()
        self.load_recipes()
        self.statusBar.showMessage("Фильтры сброшены", 2000)

    def load_recipes(self):
        """Загружает рецепты с учетом фильтров и группирует по типам блюд"""
        try:
            logger.info("=== ЗАГРУЗКА РЕЦЕПТОВ ===")

            # Получаем значения фильтров
            cuisine = self.cuisine_filter.currentText()
            if cuisine == "Любая кухня":
                cuisine = None

            time_filter = self.time_filter.currentText()
            max_time = None
            if time_filter != "Любое":
                time_map = {
                    "15 мин": 15,
                    "30 мин": 30,
                    "60 мин": 60,
                    "90 мин": 90,
                    "120 мин": 120
                }
                max_time = time_map.get(time_filter)

            favorites_only = self.favorites_only.isChecked()
            cooked_only = self.cooked_only.isChecked()

            # Используем выбранные ингредиенты
            ingredient_filter = self.selected_ingredients if hasattr(self, 'selected_ingredients') else []

            name_filter = self.name_filter.text().strip()

            logger.info(f"Активные фильтры: кухня={cuisine}, время={max_time}, "
                        f"избранное={favorites_only}, приготовлено={cooked_only}, "
                        f"ингредиенты={ingredient_filter}, название={name_filter}")

            # Получаем сгруппированные рецепты
            grouped_recipes = self.db.get_recipes_with_filters(
                self.user_id,
                cuisine=cuisine,
                max_time=max_time,
                favorites_only=favorites_only,
                cooked_only=cooked_only,
                ingredient_filter=ingredient_filter,
                name_filter=name_filter
            )

            # Проверяем, что grouped_recipes не является None
            if grouped_recipes is None:
                logger.error("Ошибка: grouped_recipes равен None")
                grouped_recipes = {}

            logger.info(f"Найдено групп: {len(grouped_recipes)}")

            # Отображаем рецепты по категориям
            self.display_recipes_by_category(grouped_recipes)

            # После загрузки рецептов обновляем подсказки
            self.load_search_suggestions()

        except Exception as e:
            logger.error(f"Ошибка при загрузке рецептов: {e}", exc_info=True)
            self.show_error_message(f"Ошибка загрузки рецептов: {str(e)}")

    def display_recipes_by_category(self, grouped_recipes):
        """Отображает рецепты, сгруппированные по категориям"""
        # Полностью очищаем контейнер
        self.clear_recipe_container()

        # Если рецептов нет
        if not grouped_recipes:
            self.show_no_recipes_message()
            return

        priority_categories = [
            "Салаты",
            "Десерты",
            "Основные блюда",
            "Завтраки",
            "Гарниры",
            "Супы",
            "Закуски",
            "Напитки",
            "Соусы"
        ]

        total_recipes = 0

        # Сначала показываем приоритетные категории в заданном порядке
        for category in priority_categories:
            if category in grouped_recipes and grouped_recipes[category]:
                recipes = grouped_recipes[category]
                total_recipes += len(recipes)
                self.create_category_section(category, recipes)
                # Удаляем категорию из grouped_recipes, чтобы не показывать её дважды
                del grouped_recipes[category]

        # Затем показываем оставшиеся категории в алфавитном порядке
        other_categories = sorted(grouped_recipes.keys())
        for category in other_categories:
            if grouped_recipes[category]:
                recipes = grouped_recipes[category]
                total_recipes += len(recipes)
                self.create_category_section(category, recipes)

        # Добавляем растягивающийся спейсер в конец
        self.recipes_container_layout.addStretch()

        self.statusBar.showMessage(f"Загружено рецептов: {total_recipes}", 3000)

    def create_category_section(self, category, recipes):
        """Создает секцию для категории с рецептами"""
        category_section = QWidget()
        category_section.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)

        category_layout = QVBoxLayout(category_section)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(10)

        # Заголовок категории
        header = QLabel(f"{self.get_category_icon(category)} {category} ({len(recipes)})")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(52, 152, 219, 0.1), 
                    stop:1 rgba(46, 204, 113, 0.1));
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }
        """)
        category_layout.addWidget(header)

        # Контейнер для карточек этой категории
        cards_container = QWidget()
        cards_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)

        # Используем FlowLayout для карточек
        flow_layout = FlowLayout(cards_container, margin=15, h_spacing=15, v_spacing=15)
        cards_container.setLayout(flow_layout)

        # Добавляем карточки
        for recipe in recipes:
            card = RecipeCard(recipe, self.db, self)
            flow_layout.addWidget(card)
            self.current_recipe_cards.append(card)

        category_layout.addWidget(cards_container)

        # Добавляем разделитель между категориями
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #dee2e6;
                max-height: 1px;
                margin: 20px 0;
            }
        """)
        category_layout.addWidget(separator)

        # Добавляем всю секцию в основной контейнер
        self.recipes_container_layout.addWidget(category_section)

    def get_category_icon(self, category):
        """Возвращает иконку для категории"""
        icons = {
            "Салаты": "🥗",
            "Десерты": "🍰",
            "Основные блюда": "🍛",
            "Завтраки": "🍳",
            "Гарниры": "🥔",
            "Супы": "🍲",
            "Закуски": "🥪",
            "Напитки": "🥤",
            "Соусы": "🥫"
        }
        return icons.get(category, "🍽️")

    def clear_recipe_container(self):
        """Очищает контейнер рецептов"""
        # Очищаем layout контейнера
        while self.recipes_container_layout.count():
            item = self.recipes_container_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'deleteLater'):
                    widget.deleteLater()
                else:
                    widget.setParent(None)

        self.current_recipe_cards = []

    def show_no_recipes_message(self):
        """Показывает сообщение об отсутствии рецептов"""
        self.clear_recipe_container()

        message_container = QWidget()
        message_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        message_layout = QVBoxLayout(message_container)
        message_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_layout.setContentsMargins(50, 100, 50, 100)

        icon = QLabel("🔍")
        icon.setStyleSheet("font-size: 64px; color: #6c757d; opacity: 0.5;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Рецептов не найдено")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #495057;
                font-weight: 600;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel("Измените параметры фильтрации или добавьте новый рецепт")
        description.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #6c757d;
                line-height: 1.5;
            }
        """)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)

        add_button = QPushButton("➕ Добавить рецепт")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                margin-top: 30px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
            }
        """)
        add_button.clicked.connect(self.add_recipe)

        message_layout.addWidget(icon)
        message_layout.addWidget(title)
        message_layout.addWidget(description)
        message_layout.addWidget(add_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.recipes_container_layout.addWidget(message_container)
        self.recipes_container_layout.addStretch()

    def show_error_message(self, error_text):
        """Показывает сообщение об ошибке"""
        self.clear_recipe_container()

        error_container = QWidget()
        error_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        error_layout = QVBoxLayout(error_container)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_layout.setContentsMargins(50, 100, 50, 100)

        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 64px; color: #dc3545; opacity: 0.7;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Ошибка загрузки")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #dc3545;
                font-weight: 600;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(f"Не удалось загрузить рецепты:\n{error_text}")
        description.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #6c757d;
                line-height: 1.5;
                padding: 20px;
                background-color: #f8d7da;
                border-radius: 8px;
                border: 1px solid #f5c6cb;
                margin-bottom: 20px;
            }
        """)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)

        retry_button = QPushButton("🔄 Попробовать снова")
        retry_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #0056b3;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
            }
        """)
        retry_button.clicked.connect(self.load_recipes)

        error_layout.addWidget(icon)
        error_layout.addWidget(title)
        error_layout.addWidget(description)
        error_layout.addWidget(retry_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.recipes_container_layout.addWidget(error_container)
        self.recipes_container_layout.addStretch()

    def load_cuisines(self):
        """Загружает список кухонь из базы данных"""
        try:
            cuisines = self.db.get_cuisines()  # Получаем список кухонь
            self.cuisine_filter.clear()
            self.cuisine_filter.addItem("Любая кухня")

            for cuisine_id, cuisine_name in cuisines:
                self.cuisine_filter.addItem(cuisine_name)

        except Exception as e:
            logger.error(f"Ошибка загрузки кухонь: {e}")
            # Используем фиксированный список в случае ошибки
            self.cuisine_filter.addItems(["Любая кухня", "Русская", "Итальянская", "Японская",
                                          "Китайская", "Мексиканская", "Французская", "Американская"])

    def logout(self):
        """Обрабатывает выход пользователя из аккаунта с подтверждением."""
        # диалог подтверждения выхода
        reply = QMessageBox.question(
            self,
            "Подтверждение выхода",
            "Вы действительно хотите выйти из аккаунта?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # Если пользователь подтвердил выход
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_callback()

    def setup_cart_tab(self, layout):
        """Настраивает содержимое вкладки корзины покупок."""
        cart_header = QLabel("🛒 Корзина ингредиентов")
        cart_header.setStyleSheet("""
            font-size: 18px;           /* Размер шрифта */
            font-weight: bold;         /* Жирный шрифт */
            color: #2c3e50;            /* Темно-синий цвет */
            margin-bottom: 15px;       /* Нижний отступ */
        """)
        layout.addWidget(cart_header)

        # Layout для кнопок управления корзиной
        cart_buttons_layout = QHBoxLayout()

        # Кнопка добавления нового ингредиента
        add_ingredient_btn = QPushButton("➕ Добавить ингредиент")
        add_ingredient_btn.clicked.connect(self.show_add_ingredient_dialog)

        # Кнопка очистки всей корзины
        clear_cart_btn = QPushButton("🗑️ Очистить корзину")
        clear_cart_btn.clicked.connect(self.clear_cart)

        # Кнопка удаления выбранных элементов
        remove_selected_btn = QPushButton("❌ Удалить выбранные")
        remove_selected_btn.clicked.connect(self.remove_selected_items)

        # Кнопка экспорта списка покупок
        export_cart_btn = QPushButton("📄 Экспорт списка")
        export_cart_btn.clicked.connect(self.export_cart)

        # Добавляем все кнопки в layout
        cart_buttons_layout.addWidget(add_ingredient_btn)
        cart_buttons_layout.addWidget(clear_cart_btn)
        cart_buttons_layout.addWidget(remove_selected_btn)
        cart_buttons_layout.addWidget(export_cart_btn)
        cart_buttons_layout.addStretch()

        layout.addLayout(cart_buttons_layout)

        # Создаем список для отображения элементов корзины
        self.cart_list = QListWidget()
        # Устанавливаем режим выбора - без выбора элементов (используем чекбоксы)
        self.cart_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        # Устанавливаем стили для списка корзины
        self.cart_list.setStyleSheet("""
            QListWidget {
                font-size: 14px;           /* Размер шрифта */
                background-color: white;   /* Белый фон */
                border: 1px solid #dee2e6; /* Серая рамка */
                border-radius: 8px;        /* Закругленные углы */
                padding: 5px;              /* Внутренние отступы */
            }
            QListWidget::item {
                padding: 0px;              /* Без отступов у элементов */
                border-bottom: 1px solid #f1f3f4; /* Разделитель между элементами */
            }
            QListWidget::item:last {
                border-bottom: none;       /* У последнего элемента нет разделителя */
            }
        """)
        layout.addWidget(self.cart_list)

    def show_add_ingredient_dialog(self):
        """Показывает диалоговое окно для добавления нового ингредиента в корзину."""
        dialog = AddIngredientDialog(self.db, self)
        # Если диалог был принят (пользователь нажал OK)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ingredient_data = dialog.get_ingredient_data()  # Получаем данные ингредиента
            if ingredient_data:
                # Добавляем ингредиент в локальную корзину
                self.cart.append({
                    'name': ingredient_data['name'],
                    'quantity': ingredient_data['quantity'],
                    'unit': ingredient_data['unit']
                })
                self.update_cart_display()  # Обновляем отображение корзины
                self.update_profile()  # Обновляем профиль (статистику)

    def add_to_cart(self, ingredients):
        """Добавляет ингредиенты рецепта в корзину и сохраняет в базу данных."""
        try:
            success_count = 0  # Счетчик успешно добавленных ингредиентов
            # Проходим по всем ингредиентам рецепта
            for name, quantity, unit in ingredients:
                # Добавляем каждый ингредиент в бд
                success = self.db.add_cart_item(
                    self.user_id, name, quantity, unit
                )
                if success:
                    success_count += 1  # Увеличиваем счетчик при успешном добавлении

            # Если хотя бы один ингредиент был добавлен успешно
            if success_count > 0:
                # Обновляем локальную корзину из базы данных
                self.cart = self.db.get_cart_items(self.user_id)
                self.update_cart_display()  # Обновляем отображение корзины
                self.update_profile()  # Обновляем профиль
                # Показываем сообщение об успехе
                QMessageBox.information(self, "Успех", f"Добавлено {success_count} ингредиентов в корзину!")
            else:
                # Показываем сообщение об ошибке
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить ингредиенты в корзину")

        except Exception as e:
            logger.error(f"Ошибка добавления в корзину: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить в корзину")

    def remove_selected_items(self):
        """Удаляет выбранные элементы из корзины (из базы данных)."""
        try:
            items_to_remove = []  # Список элементов для удаления
            # Проходим по всем элементам в списке корзины
            for i in range(self.cart_list.count()):
                item = self.cart_list.item(i)  # Получаем элемент списка
                widget = self.cart_list.itemWidget(item)  # Получаем виджет элемента
                if widget and widget.is_checked():  # Если виджет существует и выбран
                    # Добавляем данные элемента в список для удаления
                    items_to_remove.append({
                        'name': widget.ingredient_name,
                        'unit': widget.unit
                    })

            # Если есть элементы для удаления
            if items_to_remove:
                # Удаляем элементы из базы данных
                success = self.db.remove_cart_items(self.user_id, items_to_remove)
                if success:
                    # Обновляем локальную корзину из базы данных
                    self.cart = self.db.get_cart_items(self.user_id)
                    self.update_cart_display()  # Обновляем отображение корзины
                    self.update_profile()  # Обновляем профиль
                    QMessageBox.information(self, "Успех", f"Удалено {len(items_to_remove)} ингредиентов")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить элементы из корзины")
            else:
                QMessageBox.information(self, "Информация", "Не выбраны ингредиенты для удаления")

        except Exception as e:
            logger.error(f"Ошибка удаления из корзину: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось удалить элементы")

    def clear_cart(self):
        """Очищает всю корзину пользователя (из базы данных)."""
        try:
            # Если корзина уже пуста
            if not self.cart:
                QMessageBox.information(self, "Информация", "Корзина уже пуста")
                return

            # Показываем диалог подтверждения очистки
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Вы действительно хотите очистить корзину?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            # Если пользователь подтвердил очистку
            if reply == QMessageBox.StandardButton.Yes:
                # Очищаем корзину в базе данных
                success = self.db.clear_cart(self.user_id)
                if success:
                    # Очищаем локальную корзину
                    self.cart = []
                    self.update_cart_display()  # Обновляем отображение
                    self.update_profile()  # Обновляем профиль
                    # Показываем сообщение об успехе
                    QMessageBox.information(self, "Успех", "Корзина очищена!")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось очистить корзину")

        except Exception as e:
            logger.error(f"Ошибка очистки корзины: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось очистить корзину")

    def update_cart_display(self):
        """Обновляет отображение корзины с данными из базы данных."""
        self.cart_list.clear()  # Очищаем список корзины

        # Если корзина пуста
        if not self.cart:
            # Создаем элемент списка с сообщением о пустой корзине
            empty_item = QListWidgetItem("🛒 Корзина пуста")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # Запрещаем выбор
            empty_item.setForeground(QColor(108, 117, 125))  # Серый цвет текста
            self.cart_list.addItem(empty_item)  # Добавляем элемент в список
            return

        # Группируем ингредиенты по названию и единице измерения
        ingredient_groups = {}
        for item in self.cart:
            name = item['name']
            quantity = item['quantity']
            unit = item['unit']
            key = (name, unit)  # Ключ для группировки - название + единица измерения

            if key in ingredient_groups:  # Если такой ингредиент уже есть
                # Пытаемся сложить количества
                try:
                    # Преобразуем существующее количество в число
                    existing_qty = float(ingredient_groups[key]) if str(ingredient_groups[key]).replace('.',
                                                                                                        '').isdigit() else 0
                    # Преобразуем новое количество в число
                    new_qty = float(quantity) if str(quantity).replace('.', '').isdigit() else 0
                    ingredient_groups[key] = existing_qty + new_qty  # Суммируем
                except:
                    # Если не получается сложить, оставляем первое значение
                    pass
            else:
                ingredient_groups[key] = quantity  # Добавляем новый ингредиент

        # Создаем виджеты с чекбоксами для каждого ингредиента
        for (name, unit), total_quantity in ingredient_groups.items():
            # Создаем виджет элемента корзины
            item_widget = CartItemWidget(name, total_quantity, unit)
            list_item = QListWidgetItem()  # Создаем элемент списка
            list_item.setSizeHint(item_widget.sizeHint())  # Устанавливаем размер
            list_item.setBackground(QColor(248, 249, 250))  # Светло-серый фон
            self.cart_list.addItem(list_item)  # Добавляем элемент в список
            self.cart_list.setItemWidget(list_item, item_widget)  # Устанавливаем виджет для элемента

    def clear_recipe_cards(self):
        """Очищает все карточки рецептов из layout и удаляет их."""
        # Проходим по всем карточкам
        for card in self.current_recipe_cards:
            self.flow_layout.removeWidget(card)  # Удаляем из layout
            card.deleteLater()  # Удаляем виджет
        self.current_recipe_cards.clear()  # Очищаем список

    def center_cards(self):
        """Центрирует карточки, если их мало (менее 4)."""
        if len(self.current_recipe_cards) < 4:
            # Создаем контейнер с горизонтальным layout для центрирования
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)  # Без отступов

            # Добавляем растягивающееся пространство слева
            container_layout.addStretch()

            # Добавляем все карточки
            for card in self.current_recipe_cards:
                container_layout.addWidget(card)

            # Добавляем растягивающееся пространство справа
            container_layout.addStretch()

            # Очищаем FlowLayout и добавляем контейнер с центрированными карточками
            self.clear_recipe_cards()
            self.flow_layout.addWidget(container)

    def update_profile(self):
        """Обновляет данные профиля пользователя."""
        try:
            # Загружаем данные профиля из базы данных
            profile_data = self.db.get_user_profile(self.user_id)
            if profile_data:
                # Только имя пользователя
                profile_text = f"""
                    <div style="text-align: center; padding: 10px;">
                        <h2 style="margin: 0; color: #2c3e50;">👤 {profile_data['login']}</h2>
                    </div>
                    """
                self.profile_info.setText(profile_text)

                # Статистика остаётся полной
                stats_text = f"""
                    <b>📊 Ваша статистика:</b><br><br>
                    📖 <b>Всего рецептов:</b> {profile_data['recipes_count']}<br>
                    ❤️ <b>В избранном:</b> {profile_data['favorites_count']}<br>
                    ✅ <b>Приготовлено:</b> {profile_data['cooked_count']}<br>
                    🛒 <b>В корзине:</b> {profile_data['cart_count']}<br>
                    """
                self.stats_label.setText(stats_text)

            # Загружаем избранные рецепты
            self.load_favorite_recipes()

            # Загружаем приготовленные рецепты
            self.load_cooked_recipes()

        except Exception as e:
            logger.error(f"Ошибка при обновлении профиля: {e}")

    def load_favorite_recipes(self):
        """Загружает избранные рецепты пользователя."""
        # Очищаем предыдущие карточки избранных рецептов
        for i in reversed(range(self.favorites_layout.count())):
            item = self.favorites_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()  # Удаляем виджет

        try:
            # Получаем избранные рецепты из базы данных
            favorite_recipes = self.db.get_favorite_recipes(self.user_id)
            if favorite_recipes:
                # Создаем карточки для каждого избранного рецепта
                for recipe in favorite_recipes:
                    card = ProfileRecipeCard(recipe, self.db, self)  # Создаем карточку
                    self.favorites_layout.addWidget(card)  # Добавляем в layout
            else:
                # Если нет избранных рецептов, показываем сообщение
                no_favorites_label = QLabel("Нет избранных рецептов")
                no_favorites_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Выравнивание по центру
                no_favorites_label.setStyleSheet("color: #6c757d; font-size: 14px; padding: 40px;")  # Стили
                self.favorites_layout.addWidget(no_favorites_label)  # Добавляем метку
        except Exception as e:
            print(f"Ошибка при загрузке избранных рецептов: {e}")

    def load_cooked_recipes(self):
        """Загружает приготовленные рецепты пользователя."""
        # Очищаем предыдущие карточки приготовленных рецептов
        for i in reversed(range(self.cooked_layout.count())):
            item = self.cooked_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()  # Удаляем виджет

        try:
            # Получаем приготовленные рецепты из базы данных
            cooked_recipes = self.db.get_cooked_recipes(self.user_id)
            if cooked_recipes:
                # Создаем карточки для каждого приготовленного рецепта
                for recipe in cooked_recipes:
                    card = ProfileRecipeCard(recipe, self.db, self)  # Создаем карточку
                    self.cooked_layout.addWidget(card)  # Добавляем в layout
            else:
                # Если нет приготовленных рецептов, показываем сообщение
                no_cooked_label = QLabel("Нет приготовленных рецептов")
                no_cooked_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_cooked_label.setStyleSheet("color: #6c757d; font-size: 14px; padding: 40px;")
                self.cooked_layout.addWidget(no_cooked_label)  # Добавляем метку
        except Exception as e:
            print(f"Ошибка при загрузке приготовленных рецептов: {e}")

    def change_avatar(self):
        """Позволяет пользователю изменить аватар."""
        # Открываем диалог выбора файла изображения
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выбрать аватар", "", "Images (*.png *.jpg *.jpeg *.bmp);;All files (*)"
        )

        # Если файл выбран
        if file_name:
            try:
                # Читаем файл изображения как бинарные данные
                with open(file_name, 'rb') as f:
                    avatar_data = f.read()

                # Пытаемся обновить аватар в базе данных
                success = self.db.update_user_avatar(self.user_id, avatar_data)
                if success:
                    # Показываем сообщение об успехе и обновляем профиль
                    QMessageBox.information(self, "Успех", "Аватар успешно обновлен!")
                    self.update_profile()
                else:
                    # Показываем сообщение об ошибке
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить аватар")
            except Exception as e:
                # Показываем сообщение об ошибке загрузки файла
                QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке аватара: {e}")

    def open_settings(self):
        """Открывает диалог настроек приложения."""
        try:
            # Создаем диалог настроек
            dialog = SettingsDialog(self.db, self.user_id, self)
            # Подключаем сигнал обновления настроек к методу применения настроек
            dialog.settings_updated.connect(self.apply_settings)
            dialog.exec()  # Показываем диалог
        except Exception as e:
            logger.error(f"Ошибка открытия настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть настройки: {str(e)}")

    def apply_settings(self, settings_data):
        """Применяет настройки из диалога настроек."""
        try:
            # Получаем настройки шрифтов
            font_size = settings_data.get('font_size', 10)  # Размер основного шрифта
            title_font_size = settings_data.get('title_font_size', 14)  # Размер шрифта заголовков

            # Обновляем стили приложения
            self.update_styles(font_size, title_font_size)

            # Обновляем отображение изображений (показать/скрыть)
            show_images = settings_data.get('show_images', True)
            if not show_images:
                self.hide_images()  # Скрываем изображения
            else:
                self.show_images()  # Показываем изображения

            # Перезагружаем рецепты для применения изменений
            self.load_recipes()

            # Показываем сообщение об успешном применении настроек
            QMessageBox.information(self, "Успех", "Настройки применены!")

        except Exception as e:
            logger.error(f"Ошибка применения настроек: {e}")
            QMessageBox.warning(self, "Ошибка", "Не удалось применить некоторые настройки")

    def update_styles(self, font_size=10, title_font_size=14):
        """Обновляет стили приложения с новыми размерами шрифтов."""
        try:
            # Формируем строку стилей с заданными размерами шрифтов
            base_style = f"""
                QMainWindow {{
                    background-color: #f8f9fa;          /* Светло-серый фон главного окна */
                }}
                QWidget {{
                    font-family: 'Segoe UI', Arial, sans-serif;  /* Шрифт для всех виджетов */
                    font-size: {font_size}px;                    /* Размер основного шрифта */
                }}
                QTabWidget::pane {{
                    border: 1px solid #dee2e6;          /* Рамка вокруг области вкладок */
                    background-color: white;            /* Белый фон */
                    border-radius: 8px;                 /* Закругленные углы */
                }}
                QTabBar::tab {{
                    background-color: #e9ecef;          /* Светло-серый фон вкладок */
                    color: #495057;                     /* Темно-серый цвет текста */
                    padding: 8px 16px;                  /* Внутренние отступы */
                    margin-right: 2px;                  /* Отступ между вкладками */
                    border-top-left-radius: 4px;        /* Закругление верхних углов */
                    border-top-right-radius: 4px;       /* Закругление верхних углов */
                    font-size: {font_size}px;           /* Размер шрифта вкладок */
                }}
                QTabBar::tab:selected {{
                    background-color: white;            /* Белый фон выбранной вкладки */
                    color: #495057;                     /* Темно-серый цвет текста */
                    border-bottom: 2px solid #007bff;   /* Синяя полоска снизу */
                }}
                QPushButton {{
                    background-color: #007bff;          /* Синий фон кнопок */
                    color: white;                       /* Белый текст */
                    border: none;                       /* Без рамки */
                    padding: 8px 16px;                  /* Внутренние отступы */
                    border-radius: 4px;                 /* Закругленные углы */
                    font-weight: 500;                   /* Средняя жирность шрифта */
                    font-size: {font_size}px;           /* Размер шрифта кнопок */
                }}
                QPushButton:hover {{
                    background-color: #0056b3;          /* Темно-синий фон при наведении */
                }}
                QLabel {{
                    font-size: {font_size}px;           /* Размер шрифта меток */
                }}
                QLineEdit, QTextEdit, QSpinBox, QComboBox {{
                    font-size: {font_size}px;           /* Размер шрифта элементов ввода */
                    padding: 6px;                       /* Внутренние отступы */
                }}
                .header {{
                    font-size: {title_font_size}px;     /* Размер шрифта заголовков */
                    font-weight: bold;                  /* Жирный шрифт для заголовков */
                }}
            """
            self.setStyleSheet(base_style)  # Применяем стили

        except Exception as e:
            logger.error(f"Ошибка обновления стилей: {e}")

    def hide_images(self):
        """Скрывает изображения рецептов (заглушка для будущей реализации)."""
        logger.info("Функция скрытия изображений рецептов")  # Логируем вызов

    def show_images(self):
        """Показывает изображения рецептов (заглушка для будущей реализации)."""
        logger.info("Функция показа изображений рецептов")  # Логируем вызов

    def open_help(self):
        """Открывает диалог справки приложения."""
        try:
            # Создаем диалог справки
            dialog = HelpDialog(self)
            dialog.exec()  # Показываем диалог
        except Exception as e:
            logger.error(f"Ошибка открытия справки: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть справку")

    def on_settings_updated(self):
        """Обработчик обновления настроек (запрос перезагрузки приложения)."""
        QMessageBox.information(self, "Перезагрузка", "Пожалуйста, перезапустите приложение для применения настроек.")

    def refresh_data(self):
        """Обновляет все данные приложения (рецепты, профиль, корзину)."""
        self.load_recipes()  # Загружаем рецепты
        self.update_profile()  # Обновляем профиль
        self.update_cart_display()  # Обновляем корзину
        # Показываем сообщение в статус-баре на 3 секунды
        self.statusBar.showMessage("Данные обновлены", 3000)

    def add_recipe(self):
        """Открывает диалог добавления нового рецепта и обновляет автодополнение"""
        try:
            dialog = RecipeDialog(self.db, self.user_id)
            dialog.recipe_saved.connect(self.load_recipes)
            dialog.recipe_saved.connect(self.update_profile)
            dialog.exec()
        except Exception as e:
            print(f"Ошибка при добавлении рецепта: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении рецепта: {e}")

    def view_recipe(self, recipe_data):
        """Открывает диалог просмотра рецепта в виде карточки."""
        try:
            # Создаем диалог карточки рецепта
            dialog = RecipeCardDialog(recipe_data, self.db, self.user_id)
            # Подключаем сигналы диалога к методам главного окна
            dialog.add_to_cart.connect(self.add_to_cart)  # Добавление в корзину
            dialog.recipe_updated.connect(self.load_recipes)  # Обновление рецептов
            dialog.recipe_deleted.connect(self.on_recipe_deleted)  # Удаление рецепта
            dialog.exec()  # Показываем диалог
        except Exception as e:
            print(f"Ошибка при просмотре рецепта: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при просмотре рецепта: {e}")

    def on_recipe_deleted(self, recipe_id):
        """Обработчик удаления рецепта."""
        self.load_recipes()  # Обновляем список рецептов
        self.update_profile()  # Обновляем профиль
        # Показываем сообщение об успешном удалении
        QMessageBox.information(self, "Успех", "Рецепт успешно удален!")

    def export_cart(self):
        """Экспортирует список покупок в текстовый файл."""
        # Если корзина пуста
        if not self.cart:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста!")
            return

        try:
            # Открываем диалог сохранения файла
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Сохранить список покупок", "список_покупок.txt", "Text files (*.txt)"
            )

            # Если файл выбран
            if file_name:
                # Открываем файл для записи с кодировкой UTF-8
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write("Список покупок:\n")  # Заголовок
                    f.write("=" * 50 + "\n\n")  # Разделитель

                    # Группируем ингредиенты
                    ingredient_groups = {}
                    for item in self.cart:
                        name = item['name']
                        quantity = item['quantity']
                        unit = item['unit']
                        key = (name, unit)  # Ключ для группировки
                        if key in ingredient_groups:
                            # Пытаемся сложить количества
                            try:
                                ingredient_groups[key] += float(quantity)
                            except:
                                # Если не получается сложить, оставляем как есть
                                ingredient_groups[key] = quantity
                        else:
                            try:
                                ingredient_groups[key] = float(quantity)
                            except:
                                ingredient_groups[key] = quantity

                    # Записываем сгруппированные ингредиенты в файл
                    for (name, unit), total_quantity in ingredient_groups.items():
                        if isinstance(total_quantity, float):
                            f.write(f"• {name}: {total_quantity:.1f} {unit}\n")
                        else:
                            f.write(f"• {name}: {total_quantity} {unit}\n")

                # Показываем сообщение об успехе
                QMessageBox.information(self, "Успех", f"Список сохранен в файл: {file_name}")
        except Exception as e:
            # Показываем сообщение об ошибке экспорта
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать список: {e}")

    def update_stats(self):
        """Обновление статистики (псевдоним для update_profile)."""
        self.update_profile()

    def resizeEvent(self, event):
        """Обработчик события изменения размера окна."""
        super().resizeEvent(event)

        # При изменении размера окна обновляем FlowLayout
        if hasattr(self, 'current_recipe_cards') and self.current_recipe_cards:
            # Перезагружаем рецепты для корректного перераспределения карточек
            QTimer.singleShot(100, self.load_recipes)