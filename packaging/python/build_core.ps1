$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location $root

python -m pip install --upgrade pip pyinstaller
python -m PyInstaller --clean --noconfirm packaging/python/desktop_server.spec

New-Item -ItemType Directory -Force -Path dist\core | Out-Null
Copy-Item -Recurse -Force dist\JelonCore\* dist\core\
Write-Host 'JelonCore packaged in dist/core'
