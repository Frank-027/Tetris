# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['tetris_noESP.py'],
    pathex=[],
    binaries=[],
    datas=[('Tetris.mp3', '.'), ('clear.wav', '.')],
    hiddenimports=[],
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
    name='tetris_noESP',
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
    icon=['tetris_icoon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tetris_noESP',
)
app = BUNDLE(
    coll,
    name='tetris_noESP.app',
    icon='tetris_icoon.icns',
    bundle_identifier=None,
)
