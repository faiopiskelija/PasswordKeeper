# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Cryptography
datas_crypto, binaries_crypto, hiddenimports_crypto = collect_all('cryptography')

# PySide6 (Qt plugins, platforms и т.д.)
datas_qt, binaries_qt, hiddenimports_qt = collect_all('PySide6')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries_crypto + binaries_qt,
    datas=[
        ('*.ui', '.'),
        ('*.png', '.'),
        ('mainDB.db', '.'),
    ] + datas_crypto + datas_qt,
    hiddenimports=hiddenimports_crypto + hiddenimports_qt,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PasswordKeeper',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='main.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='PasswordKeeper'
)