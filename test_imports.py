"""
Скрипт для проверки импортов перед сборкой
"""

import os
import sys

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Проверка импортов...")

    # Проверяем основные модули
    from src.database import DataBase

    print("✓ DataBase загружен")

    from src.modules.recipe_dialog import RecipeDialog, RecipeCardDialog

    print("✓ RecipeDialog и RecipeCardDialog загружены")

    from src.main_window import MainWindow

    print("✓ MainWindow загружен")

    print("\n✅ Все импорты успешны!")

except Exception as e:
    print(f"\n❌ Ошибка импорта: {e}")
    import traceback

    traceback.print_exc()