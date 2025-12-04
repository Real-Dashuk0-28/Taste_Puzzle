@echo off
echo Сборка Taste_Pazzle в EXE файл...
echo.

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist


pyinstaller ^
  --onefile ^
  --windowed ^
  --icon=img/ico2.ico ^
  --name=Taste_Pazzle ^
  --add-data="data;data" ^
  --add-data="img;img" ^
  --hidden-import=sqlalchemy.ext.declarative ^
  --hidden-import=sqlalchemy.orm ^
  --hidden-import=sqlalchemy.sql ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  --hidden-import=PIL ^
  --hidden-import=PIL.Image ^
  --hidden-import=PIL.ImageDraw ^
  src/main.py

echo.
echo Сборка завершена!
echo EXE файл: dist\Taste_Pazzle.exe
pause