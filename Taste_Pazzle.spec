# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\data\\Taste_Pazzle.db', 'data'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\help_icon.png', 'img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\ico2.ico', 'img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\icon.ico', 'img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\refresh_icon.png', 'img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\search_icon.png', 'img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\settings_icon.png', 'img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img\\apple_pie.jpg', 'img/recipe_img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img\\cabbage_rolls.jpg', 'img/recipe_img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img\\caesar.jpg', 'img/recipe_img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img\\french_toast.jpg', 'img/recipe_img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img\\mashed_potatoes.jpg', 'img/recipe_img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img\\olivier.jpg', 'img/recipe_img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img\\pasta_carbonara.jpg', 'img/recipe_img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img\\ramen.jpg', 'img/recipe_img')],
    hiddenimports=['sqlalchemy.ext.declarative', 'sqlalchemy.orm', 'sqlalchemy.sql', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PIL', 'PIL.Image', 'PIL.ImageDraw'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Taste_Pazzle',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\ico2.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Taste_Pazzle',
)
