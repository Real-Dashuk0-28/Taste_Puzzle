# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\*', 'img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img', 'img/recipe_img')],
    hiddenimports=['modules.recipe_dialog', 'modules.settings_dialog', 'modules.help_dialog', 'modules.add_ingredient_dialog', 'sqlalchemy', 'sqlalchemy.orm', 'sqlalchemy.ext.declarative', 'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'logging', 'base64', 'io'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TastePuzzle',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\ico2.ico'],
)
