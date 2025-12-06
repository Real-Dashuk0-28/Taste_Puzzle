# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\*', 'img'), ('C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\recipe_img\\*', 'img/recipe_img')],
    hiddenimports=['sqlalchemy', 'PIL'],
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
    a.binaries,
    a.datas,
    [],
    name='TastePuzzle_Debug',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Panda\\PycharmProjects\\Taste_Puzzle\\img\\ico2.ico'],
)
