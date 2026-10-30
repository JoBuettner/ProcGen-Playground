"""Replay release API failures without credentials or network calls."""

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.mark.parametrize("scenario,expected_creates,success", [
    ("transient", 2, True), ("committed-before-500", 1, True),
    ("persistent", 3, False), ("validation", 1, False),
    ("published", 0, True), ("wrong-target", 0, False),
])
def test_release_failure_recovery(tmp_path: Path, scenario: str, expected_creates: int, success: bool) -> None:
    publisher = Path(__file__).resolve().parents[1] / "scripts/publish_prerelease.ps1"
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "0.2.0.dev0"\n')
    (tmp_path / ".artifacts").mkdir()
    notice = tmp_path / "docs/licensing/THIRD-PARTY-NOTICES.txt"
    notice.parent.mkdir(parents=True)
    notice.write_text("Fixture licensing notice")
    (tmp_path / "dist").mkdir()
    for name in ("ProcGenPlayground-Windows-x64-portable.zip", "ProcGenPlayground-corresponding-sources.zip"):
        for suffix in ("", ".sha256"):
            (tmp_path / "dist" / (name + suffix)).write_bytes(b"fixture")
    harness = tmp_path / "replay.ps1"
    harness.write_text(r'''
$ErrorActionPreference = 'Stop'
$global:calls = @()
$global:creates = 0
$global:draft = $env:TEST_SCENARIO -eq 'wrong-target'
function Start-Sleep { param($Seconds) }
function gh {
    $global:calls += ,@($args)
    $global:LASTEXITCODE = 0
    switch ($args[1]) {
        'view' {
            if ($env:TEST_SCENARIO -eq 'published' -or $global:draft) {
                return (@{isDraft=($env:TEST_SCENARIO -ne 'published'); url='https://example.invalid/release';
                    targetCommitish=$(if ($env:TEST_SCENARIO -eq 'wrong-target') {'wrong'} else {$env:GITHUB_SHA})} | ConvertTo-Json)
            }
            $global:LASTEXITCODE = 1
            return 'release not found'
        }
        'create' {
            $global:creates++
            if ($env:TEST_SCENARIO -eq 'committed-before-500') { $global:draft = $true }
            if ($env:TEST_SCENARIO -eq 'validation') { $global:LASTEXITCODE = 1; return 'HTTP 422: Validation Failed' }
            if ($env:TEST_SCENARIO -eq 'persistent' -or $global:creates -eq 1) {
                $global:LASTEXITCODE = 1
                return 'HTTP 500: Internal Server Error'
            }
            $global:draft = $true
        }
        'upload' { if (-not $global:draft) { throw 'Upload without a verified draft' } }
        'edit' { if (-not $global:draft) { throw 'Publish without a verified draft' } }
        default { throw 'Unexpected gh command' }
    }
}
$succeeded = $false
$failure = ''
try { & $env:TEST_PUBLISHER; $succeeded = $true } catch { $failure = $_.Exception.Message }
@{success=$succeeded; creates=$global:creates; calls=$global:calls; error=$failure} |
    ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 result.json
''', encoding="utf-8")
    environment = dict(os.environ, GITHUB_SHA="0123456789abcdef0123456789abcdef01234567",
                       GH_REPO="example/repo", GITHUB_SERVER_URL="https://github.com",
                       TEST_SCENARIO=scenario, TEST_PUBLISHER=str(publisher))
    subprocess.run([shutil.which("pwsh") or "powershell.exe", "-NoProfile", "-File", str(harness)],
                   cwd=tmp_path, env=environment, check=True, capture_output=True, text=True, timeout=20)
    result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8-sig"))
    assert result["success"] is success, result
    assert result["creates"] == expected_creates
    calls = result["calls"]
    uploads = [call for call in calls if call[1] == "upload"]
    publishes = [call for call in calls if call[1] == "edit"]
    if success and scenario != "published":
        assert len(uploads) == len(publishes) == 1
        assert len([arg for arg in uploads[0] if arg.startswith("dist/")]) == 4
    else:
        assert not uploads and not publishes
    for call in calls:
        if call[1] == "create":
            assert "--draft" in call and "--prerelease" in call
            assert not any(arg.startswith("dist/") or arg.startswith("--latest") for arg in call)
