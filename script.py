import subprocess

# Ottieni tutte le librerie installate
result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE)
installed_packages = result.stdout.decode('utf-8').split('\n')

# Estrai i nomi delle librerie
all_libraries = [pkg.split('==')[0] for pkg in installed_packages if pkg]

# Librerie che vuoi includere
hidden_imports = ['numpy', 'pandas']

# Rimuovi le librerie che vuoi includere da all_libraries
all_libraries = [lib for lib in all_libraries if lib not in hidden_imports]

# Scrivi il file .spec
with open('your_script.spec', 'w') as f:
    f.write(f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['your_script.py'],
    pathex=['/path/to/your/script'],
    binaries=[],
    datas=[],
    hiddenimports={hidden_imports},
    hookspath=[],
    runtime_hooks=[],
    excludes={all_libraries},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='your_executable_name',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='your_executable_name',
)
""")