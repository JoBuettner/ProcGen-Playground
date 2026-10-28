param(
    [string]$Python = (Join-Path $PSScriptRoot '..\.venv\Scripts\python.exe')
)

$ErrorActionPreference = 'Stop'
$Python = (Resolve-Path -LiteralPath $Python).Path
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path

function Invoke-Python {
    param([string[]]$Arguments)
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed ($LASTEXITCODE): $Arguments"
    }
}

Push-Location -LiteralPath $projectRoot
try {
    New-Item -ItemType Directory -Force .artifacts | Out-Null
    Invoke-Python -Arguments @('-c', 'import sys,struct; assert sys.version_info[:2] == (3,10) and struct.calcsize("P") == 8 and sys.platform == "win32", "Windows x64 / Python 3.10 required"')
    Invoke-Python -Arguments @('-m', 'pip', 'check')
    Invoke-Python -Arguments @('-m', 'pytest', '-q')
    Invoke-Python -Arguments @('-m', 'mypy')
    Invoke-Python -Arguments @('scripts/prepare_license_sources.py', '--download')
    Invoke-Python -Arguments @('scripts/prepare_windows_runtime.py', '--download')
    Invoke-Python -Arguments @('scripts/collect_licenses.py')
    Invoke-Python -Arguments @('scripts/verify_upstream.py')
    Invoke-Python -Arguments @('-m', 'PyInstaller', '--noconfirm', '--clean', 'packaging/procgen-playground.spec')
    Invoke-Python -Arguments @('scripts/package_portable.py')
    Invoke-Python -Arguments @('scripts/package_sources.py')
    Invoke-Python -Arguments @('scripts/verify_license_bundle.py')
    Invoke-Python -Arguments @('scripts/verify_frozen.py', '--all')
}
finally {
    Pop-Location
}
