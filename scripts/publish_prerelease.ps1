$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$version = & .\.venv\Scripts\python.exe -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb'))['project']['version'])"
if ($LASTEXITCODE -ne 0) { throw 'Could not read application version' }
if ($env:GITHUB_SHA -notmatch '^[0-9a-f]{40}$') { throw 'A full workflow commit SHA is required' }
if (-not $env:GH_REPO) { throw 'GH_REPO is required' }
$tag = 'v' + $version.Trim().Replace('.dev', '-dev.') + '-g' + $env:GITHUB_SHA.Substring(0, 12)
$assets = @(
    'dist/ProcGenPlayground-Windows-x64-portable.zip',
    'dist/ProcGenPlayground-Windows-x64-portable.zip.sha256',
    'dist/ProcGenPlayground-corresponding-sources.zip',
    'dist/ProcGenPlayground-corresponding-sources.zip.sha256'
)
foreach ($asset in $assets) {
    if (-not (Test-Path -LiteralPath $asset -PathType Leaf)) { throw "Release file missing: $asset" }
}

# A completed release is immutable from this workflow's perspective. A failed
# upload may leave a draft, which can be completed by rerunning the same commit.
$existingJson = & gh release view $tag --json isDraft,url,targetCommitish 2>$null
$exists = $LASTEXITCODE -eq 0
if ($exists) {
    $existing = $existingJson | ConvertFrom-Json
    if (-not $existing.isDraft) {
        Write-Output "Release already published; leaving its assets unchanged: $($existing.url)"
        exit 0
    }
    if ($existing.targetCommitish -ne $env:GITHUB_SHA) {
        throw 'Existing draft targets another commit; refusing to change it'
    }
}

$notesPath = '.artifacts/release-notes.md'
$notes = @"
Automatic development prerelease of ProcGen Playground $version.

Commit: $($env:GITHUB_SHA)

Download the Windows portable ZIP, extract the entire folder, and run
ProcGenPlayground.exe. Requires Windows 10/11 x64, an AVX-capable CPU and
an OpenGL 3.3 graphics driver. No Python installation is required.

The matching source ZIP and SHA-256 files are attached to this release.
Both ZIPs passed automated checks; CI does not establish desktop gameplay testing.

Microsoft component terms:
$($env:GITHUB_SERVER_URL)/$($env:GH_REPO)/blob/$($env:GITHUB_SHA)/third_party/microsoft/DOWNSTREAM-TERMS.md

"@
$notes += [Environment]::NewLine + (Get-Content -Raw -LiteralPath 'docs/licensing/THIRD-PARTY-NOTICES.txt')
$notes | Set-Content -LiteralPath $notesPath -Encoding utf8

if ($exists) {
    & gh release upload $tag @assets --clobber
    if ($LASTEXITCODE -ne 0) { throw 'Draft release upload failed' }
} else {
    & gh release create $tag @assets --draft --prerelease --latest=false `
        --target $env:GITHUB_SHA --title "ProcGen Playground $tag" --notes-file $notesPath
    if ($LASTEXITCODE -ne 0) { throw 'Draft release creation/upload failed' }
}
& gh release edit $tag --draft=false --prerelease --latest=false --notes-file $notesPath
if ($LASTEXITCODE -ne 0) { throw 'Release publication failed' }
Write-Output "Published $tag"
