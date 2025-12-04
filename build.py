import os
import shutil
import subprocess
import sys
from pathlib import Path


def build_exe():
    """Собирает проект в EXE файл с иконкой"""

    # Пути
    project_root = Path(__file__).parent
    src_dir = project_root / 'src'
    data_dir = project_root / 'data'
    img_dir = project_root / 'img'
    build_dir = project_root / 'build'
    dist_dir = project_root / 'dist'

    print("=== Начало сборки проекта ===")
    print(f"Корневая папка: {project_root}")
    print(f"Папка данных: {data_dir}")

    # Проверка существования файлов
    db_files = list(data_dir.glob('*.db'))
    print(f"Найдены файлы БД: {[f.name for f in db_files]}")

    # Проверка наличия иконки
    icon_path = img_dir / 'ico2.ico'
    if not icon_path.exists():
        print(f"ПРЕДУПРЕЖДЕНИЕ: Иконка не найдена: {icon_path}")
        # Попробуем найти другую иконку
        icon_files = list(img_dir.glob('*.ico'))
        if icon_files:
            icon_path = icon_files[0]
            print(f"Используем иконку: {icon_path}")
        else:
            print("Иконка не найдена, сборка продолжится без иконки")
            icon_path = None

    # Очистка предыдущих сборок
    for dir_path in [build_dir, dist_dir]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Очищена папка: {dir_path}")

    # Создаем список данных для включения
    datas_args = []

    # Добавляем файлы базы данных (только существующие)
    for db_file in data_dir.glob('*.db'):
        if db_file.exists():
            datas_args.extend(['--add-data', f'{db_file};data'])
            print(f"Добавлен файл БД: {db_file.name}")

    # Добавляем изображения
    for img_file in img_dir.glob('*.*'):
        if img_file.suffix.lower() in ['.png', '.ico', '.jpg', '.jpeg', '.bmp']:
            datas_args.extend(['--add-data', f'{img_file};img'])

    # Добавляем изображения рецептов
    recipe_img_dir = img_dir / 'recipe_img'
    if recipe_img_dir.exists():
        for recipe_img in recipe_img_dir.glob('*.*'):
            if recipe_img.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                datas_args.extend(['--add-data', f'{recipe_img};img/recipe_img'])

    # Базовые аргументы PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--name', 'Taste_Pazzle',
        '--windowed',  # Для GUI приложения (без консоли)
    ]

    # Добавляем иконку если она существует
    if icon_path and icon_path.exists():
        cmd.extend(['--icon', str(icon_path)])
        print(f"Используется иконка: {icon_path}")

    # Добавляем данные
    cmd.extend(datas_args)

    # Добавляем скрытые импорты
    hidden_imports = [
        'sqlalchemy.ext.declarative',
        'sqlalchemy.orm',
        'sqlalchemy.sql',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
    ]

    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])

    # Добавляем основной файл
    cmd.append(str(src_dir / 'main.py'))

    print(f"\nКоманда сборки:")
    print(' '.join(cmd))

    # Запускаем PyInstaller
    print("\nЗапуск PyInstaller...")
    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        print("=== Сборка успешно завершена ===")

        # Создаем папку с распространяемым пакетом
        package_dir = project_root / 'Taste_Pazzle_Package'
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir()

        # Копируем EXE файл
        exe_source = dist_dir / 'Taste_Pazzle.exe'
        if exe_source.exists():
            shutil.copy2(exe_source, package_dir / 'Taste_Pazzle.exe')
            print(f"Скопирован EXE файл")

        # Создаем подпапки
        (package_dir / 'data').mkdir()
        (package_dir / 'img').mkdir()
        (package_dir / 'img' / 'recipe_img').mkdir(parents=True)

        # Копируем базу данных
        for db_file in data_dir.glob('*.db'):
            if db_file.exists():
                shutil.copy2(db_file, package_dir / 'data' / db_file.name)
                print(f"Скопирован: data/{db_file.name}")

        # Копируем изображения
        for img_file in img_dir.glob('*.*'):
            if img_file.suffix.lower() in ['.png', '.ico', '.jpg', '.jpeg']:
                shutil.copy2(img_file, package_dir / 'img' / img_file.name)
                print(f"Скопирован: img/{img_file.name}")

        # Копируем изображения рецептов
        if recipe_img_dir.exists():
            for recipe_img in recipe_img_dir.glob('*.*'):
                shutil.copy2(recipe_img, package_dir / 'img' / 'recipe_img' / recipe_img.name)
                print(f"Скопирован: img/recipe_img/{recipe_img.name}")

        # Копируем README.md если есть
        if (project_root / 'README.md').exists():
            shutil.copy2(project_root / 'README.md', package_dir / 'README.md')

        print(f"\n=== Сборка завершена ===")
        print(f"Распространяемый пакет создан в: {package_dir}")
        print(f"Запускаемый файл: {package_dir / 'Taste_Pazzle.exe'}")

    else:
        print("Ошибка при сборке!")
        print(f"Код возврата: {result.returncode}")


if __name__ == "__main__":
    build_exe()