"""
Скрипт для сборки Taste Puzzle в один исполняемый файл
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_project():
    """Собирает проект в один исполняемый файл"""

    # Пути к файлам
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    img_dir = project_root / "img"
    data_dir = project_root / "data"

    print(f"Корневая директория: {project_root}")
    print(f"Директория исходного кода: {src_dir}")

    # Проверяем существование основных файлов
    if not (src_dir / "main.py").exists():
        print("Ошибка: не найден main.py в папке src/")
        return False

    if not img_dir.exists():
        print("Ошибка: не найдена папка img/")
        return False

    # Проверяем наличие иконок
    if not (img_dir / "icon.ico").exists():
        print("Предупреждение: не найдена иконка icon.ico для окон приложения")

    if not (img_dir / "ico2.ico").exists():
        print("Предупреждение: не найдена иконка ico2.ico для exe-файла")

    # Создаем папку для сборки
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"

    # Удаляем старые сборки
    for folder in [build_dir, dist_dir]:
        if folder.exists():
            print(f"Удаляем старую папку: {folder}")
            shutil.rmtree(folder)

    datas = [
        ('img/*.png', 'img'),
        ('img/*.ico', 'img'),
        ('img/*.jpg', 'img'),
        ('img/recipe_img/*', 'img/recipe_img'),
        ('data/*', 'data')
    ],

    # Команда сборки с оптимизацией
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--noconsole",
        f"--icon={img_dir / 'ico2.ico'}",
        "--name=TastePuzzle",
        # Основные ресурсы
        f"--add-data={img_dir / '*'};img",
        # Рекурсивно добавляем папку recipe_img
        f"--add-data={img_dir / 'recipe_img'};img/recipe_img",
        # Модули для избежания циклических импортов
        "--hidden-import=modules.recipe_dialog",
        "--hidden-import=modules.settings_dialog",
        "--hidden-import=modules.help_dialog",
        "--hidden-import=modules.add_ingredient_dialog",
        # Библиотеки
        "--hidden-import=sqlalchemy",
        "--hidden-import=sqlalchemy.orm",
        "--hidden-import=sqlalchemy.ext.declarative",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageDraw",
        # PyQt6 модули
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        # Другие зависимости
        "--hidden-import=logging",
        "--hidden-import=base64",
        "--hidden-import=io",
        # Оптимизация
        "--clean",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=scipy",
        "--exclude-module=tkinter",
        str(src_dir / "main.py")
    ]

    print(f"Команда сборки: {' '.join(cmd)}")

    # Запускаем сборку
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("\n✅ Сборка успешно завершена!")
            print(f"Исполняемый файл: {dist_dir / 'TastePuzzle.exe'}")

            # Создаем папку data рядом с исполняемым файлом
            data_target_dir = dist_dir / "data"
            data_target_dir.mkdir(parents=True, exist_ok=True)

            # Копируем существующую базу данных, если есть
            if data_dir.exists():
                for db_file in data_dir.glob("*.db"):
                    shutil.copy2(db_file, data_target_dir)
                    print(f"Скопирована база данных: {db_file.name}")
            else:
                print("База данных не найдена, будет создана при первом запуске")


            print("\n📦 Готово! Ваше приложение собрано в один файл.")
            print(f"Путь к исполняемому файлу: {dist_dir / 'TastePuzzle.exe'}")

            # Открываем папку с результатом
            if sys.platform == "win32":
                os.startfile(dist_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", dist_dir])
            else:
                subprocess.run(["xdg-open", dist_dir])

            return True

        else:
            print(f"\n❌ Ошибка сборки (код {result.returncode}):")
            if result.stdout:
                print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
            return False

    except Exception as e:
        print(f"\n❌ Исключение при сборке: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    build_project()