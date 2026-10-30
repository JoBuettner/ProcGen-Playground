$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$project = [regex]::Match((Get-Content -Raw pyproject.toml), '(?ms)^\[project\]\s*\n(.*?)(?=^\[|\z)').Groups[1].Value
$version = [regex]::Match($project, '(?m)^version\s*=\s*"([^"]+)"').Groups[1].Value
if (-not $version) { throw 'Could not read application version' }
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
function Get-ExistingRelease {
    $response = & gh release view $tag --json isDraft,url,targetCommitish 2>&1
    if ($LASTEXITCODE -eq 0) { return ($response -join "`n" | ConvertFrom-Json) }
    $message = $response -join "`n"
    if ($message -match 'release not found|HTTP 404') { return $null }
    throw "Could not check existing release: $message"
}

function Test-ReusableDraft($release) {
    if ($null -eq $release) { return $false }
    if (-not $release.isDraft) {
        Write-Host "Release already published; leaving its assets unchanged: $($release.url)"
        return $false
    }
    if ($release.targetCommitish -ne $env:GITHUB_SHA) {
        throw 'Existing draft targets another commit; refusing to change it'
    }
    return $true
}

$existing = Get-ExistingRelease
if ($null -ne $existing -and -not (Test-ReusableDraft $existing)) {
    return
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

if ($null -eq $existing) {
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        # Create only the draft here. Asset uploads and publication are separate,
        # recoverable operations. A prerelease does not need a make_latest field.
        $response = & gh release create $tag --draft --prerelease `
            --target $env:GITHUB_SHA --title "ProcGen Playground $tag" --notes-file $notesPath 2>&1
        if ($LASTEXITCODE -eq 0) { break }
        $message = $response -join "`n"
        Write-Host "Draft creation attempt $attempt failed: $message"
        # A 500 can occur after the server has committed the draft. Reconcile
        # before another POST, rather than creating duplicate releases.
        $existing = Get-ExistingRelease
        if ($null -ne $existing) {
            if (-not (Test-ReusableDraft $existing)) { return }
            break
        }
        if ($message -notmatch 'HTTP (500|502|503|504)\b' -or $attempt -eq 3) {
            throw "Draft release creation failed after $attempt attempt(s): $message"
        }
        Start-Sleep -Seconds (2 * $attempt)
    }
}
& gh release upload $tag @assets --clobber
if ($LASTEXITCODE -ne 0) { throw 'Draft release upload failed; rerun the release job to resume' }
& gh release edit $tag --draft=false --prerelease --notes-file $notesPath
if ($LASTEXITCODE -ne 0) { throw 'Release publication failed' }
Write-Output "Published $tag"
