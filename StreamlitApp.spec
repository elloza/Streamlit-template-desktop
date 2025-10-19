# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [('src', 'src'), ('assets', 'assets'), ('config', 'config'), ('.streamlit', '.streamlit')]
datas += copy_metadata('streamlit')
datas += copy_metadata('altair')


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[('.conda/Library/bin/libexpat.dll', '.'), ('.conda/Library/bin/ffi.dll', '.')],
    datas=datas,
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.web.bootstrap',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.app_session',
        'streamlit.runtime.state',
        'streamlit.runtime.state.session_state',
        'streamlit.proto',
        'streamlit.logger',
        'pywebview',
        'pywebview.platforms.winforms',
        'yaml',
        'watchdog',
        'click',
        'tornado',
        'altair',
        'pandas',
        'numpy',
        'PIL',
        'pydantic',
        'typing_extensions',
        'importlib.metadata',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'sklearn', 'tensorflow', 'torch'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StreamlitApp',
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
    icon=['assets\\icon_default.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StreamlitApp',
)
