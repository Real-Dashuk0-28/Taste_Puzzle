# src/resource_path.py - Утилита для получения путей к ресурсам
import sys
import os
from pathlib import Path


def resource_path(relative_path):
    """
    Получает абсолютный путь к ресурсу.
    Работает как в режиме разработки, так и в собранном exe.
    """
    try:
        # PyInstaller создает временную папку в _MEIPASS
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
        else:
            # В режиме разработки используем папку проекта
            base_path = Path(__file__).parent.parent

        # Преобразуем относительный путь
        if relative_path.startswith('img/') or relative_path.startswith('data/'):
            # Если путь начинается с папки ресурсов, ищем в правильном месте
            full_path = base_path / relative_path
        else:
            # Иначе предполагаем, что путь уже корректный
            full_path = base_path / relative_path

        # Нормализуем путь
        full_path = str(full_path).replace('\\', '/')

        return full_path

    except Exception as e:
        print(f"[RESOURCE_PATH] Ошибка: {e} для пути {relative_path}")
        # Возвращаем исходный путь как fallback
        return str(Path(relative_path))