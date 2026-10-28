param(
    [Parameter(Mandatory = $true)][string] $ArchiveDirectory,
    [Parameter(Mandatory = $true)][string] $Workspace,
    [Parameter(Mandatory = $true)][string] $ToolchainArchive
)
$ErrorActionPreference = 'Stop'
$archiveRoot = (Resolve-Path -LiteralPath $ArchiveDirectory).Path
$compilerArchive = (Resolve-Path -LiteralPath $ToolchainArchive).Path
$workRoot = [System.IO.Path]::GetFullPath($Workspace)
New-Item -ItemType Directory -Force -Path $workRoot | Out-Null
$manifest = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot '../NUMERICAL-SOURCE-MANIFEST.json') | ConvertFrom-Json

foreach ($entry in $manifest.archives) {
    if ($entry.purpose -eq 'local-toolchain-not-for-redistribution') {
        $path = $compilerArchive
    } else {
        $path = Join-Path $archiveRoot ([System.IO.Path]::GetFileName($entry.local_path))
    }
    $file = Get-Item -LiteralPath $path
    if ($file.Length -ne $entry.bytes -or (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant() -ne $entry.sha256) {
        throw "Archive size/hash mismatch: $path"
    }
}

function Expand-CheckedArchive([string] $archive, [string] $destination, [string[]] $arguments) {
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    & tar -xf $archive -C $destination @arguments
    if ($LASTEXITCODE -ne 0) { throw "tar extraction failed: $archive" }
}

$blasRoot = Join-Path $workRoot 'build/openblas'
if (-not (Test-Path -LiteralPath (Join-Path $blasRoot 'Makefile'))) {
    Expand-CheckedArchive (Join-Path $archiveRoot 'OpenBLAS-c2f4bdbbb43a1d20a7342f40122e18e573ce436a.tar.gz') $blasRoot @('--strip-components=1')
}
$gccRoot = Join-Path $workRoot 'gcc-source'
if (-not (Test-Path -LiteralPath (Join-Path $gccRoot 'gcc-10.3.0/gcc/doc/include/fdl.texi'))) {
    # These are all dependencies required for the independent libquadmath build.
    # The full, unmodified GCC archive remains in the source companion.
    $members = @('libquadmath', 'config', 'include', 'config.guess', 'config.sub',
        'config-ml.in', 'install-sh', 'ltmain.sh', 'missing', 'mkinstalldirs',
        'depcomp', 'COPYING.LIB', 'COPYING3', 'COPYING.RUNTIME', 'gcc/BASE-VER', 'gcc/doc/include') |
        ForEach-Object { "gcc-10.3.0/$_" }
    Expand-CheckedArchive (Join-Path $archiveRoot 'gcc-10.3.0.tar.xz') $gccRoot $members
}
$toolRoot = Join-Path $workRoot 'toolchain/rtools40'
if (-not (Test-Path -LiteralPath (Join-Path $toolRoot 'ucrt64/bin/gcc.exe'))) {
    Expand-CheckedArchive $compilerArchive $toolRoot @('--strip-components=1',
        'rtools40/usr', 'rtools40/ucrt64', 'rtools40/etc', 'rtools40/var')
}
New-Item -ItemType Directory -Force -Path (Join-Path $toolRoot 'tmp') | Out-Null
Get-ChildItem -LiteralPath $PSScriptRoot -File | Where-Object {
    $_.Extension -in @('.sh', '.py', '.patch', '.c')
} | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $workRoot $_.Name)
}
Write-Output "Verified source archives; build workspace: $workRoot"
Write-Output "Project-local MSYS shell: $(Join-Path $toolRoot 'usr/bin/bash.exe')"
