# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # Include application resources from the repository. Bundle the whole
    # `shared` directory so code that references paths like
    # 'shared/images/MouseLogo.png' still work when frozen.
    datas=[('shared', 'shared'), ('settings', 'settings'), ('experiment_pages', 'experiment_pages')],
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
    a.binaries,
    a.datas,
    [],
    name='Mouser',
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
    # No icon file included here because the repository does not contain a
    # Windows .ico file at the previously referenced path. If you have an
    # .ico, re-add it here (e.g. icon=['path\\to\\icon.ico']).
)
