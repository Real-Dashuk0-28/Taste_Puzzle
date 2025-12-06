"""
Очистка временных файлов сборки
"""

import os
import shutil
import glob


def cleanup():
    """Удаляет временные файлы сборки"""

    files_to_remove = [
        "TastePuzzle.spec",
        "build/",
        "dist/",
        "__pycache__/",
        "src/__pycache__/",
        "*.log",
        "*.pyc"
    ]

    for pattern in files_to_remove:
        if pattern.endswith('/'):
            # Это папка
            folder = pattern.rstrip('/')
            if os.path.exists(folder):
                shutil.rmtree(folder)
                print(f"Удалена папка: {folder}")
        else:
            # Это файлы по шаблону
            for file in glob.glob(pattern):
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Удален файл: {file}")

    print("✅ Очистка завершена!")


if __name__ == "__main__":
    cleanup()