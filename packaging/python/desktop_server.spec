from pathlib import Path

block_cipher = None

project_root = Path(SPEC).resolve().parents[2]

analysis = Analysis(
    [str(project_root / 'engine' / 'desktop_server.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / 'engine'), 'engine'),
        (str(project_root / 'skills'), 'skills'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name='JelonCore',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
