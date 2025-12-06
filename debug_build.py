"""
Скрипт для отладочной сборки с выводом консоли
"""

import os
import sys
import subprocess
from pathlib import Path


def debug_build():
    """Собирает проект с выводом консоли для отладки"""
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    img_dir = project_root / "img"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",  # Вместо --windowed для отладки
        f"--icon={img_dir / 'ico2.ico'}",
        "--name=TastePuzzle_Debug",
        f"--add-data={img_dir / '*'};img",
        f"--add-data={img_dir / 'recipe_img' / '*'};img/recipe_img",
        "--hidden-import=sqlalchemy",
        "--hidden-import=PIL",
        "--clean",
        str(src_dir / "main.py")
    ]

    print("Запуск отладочной сборки...")
    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode == 0:
        print("\n✅ Отладочная сборка завершена!")
        print("Запустите TastePuzzle_Debug.exe для просмотра ошибок в консоли.")
    else:
        print("\n❌ Ошибка отладочной сборки")


if __name__ == "__main__":
    debug_build()