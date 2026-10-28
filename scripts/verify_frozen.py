"""Check packaged native fidelity with a stripped environment and relocated ZIP.

This intentionally does not claim to verify desktop keyboard input or operation
on a separate machine without Python installed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pefile

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="compare all 96 upstream cases")
    args = parser.parse_args()
    archive_path = ROOT / "dist" / "ProcGenPlayground-Windows-x64-portable.zip"
    # Unique extraction directories prevent stale reports or a prior build from
    # satisfying this run. Include both spaces and non-ASCII path characters.
    import tempfile

    extraction = Path(tempfile.mkdtemp(prefix="Portable Prüfung ", dir=ROOT / ".artifacts"))
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(extraction)
    app = extraction / "ProcGenPlayground"
    exe = app / "ProcGenPlayground.exe"
    assert pefile.PE(str(exe)).OPTIONAL_HEADER.Subsystem == 2, "must be a windowed executable"
    import procgen

    original_data = Path(procgen.__file__).parent / "data"
    bundled_data = app / "_internal" / "procgen" / "data"
    files_checked = 0
    for original in original_data.rglob("*"):
        if not original.is_file():
            continue
        bundled = bundled_data / original.relative_to(original_data)
        assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256(bundled.read_bytes()).digest(), str(bundled)
        files_checked += 1
    assert (app / "_internal" / "gym3" / "internal" / "font.bin").is_file()
    assert (app / "_internal" / "glfw" / "glfw3.dll").is_file()
    assert (app / "_internal" / "licenses" / "third_party" / "procgen" / "ASSET_LICENSES.md").is_file()
    for notice in ("gym3/LICENSE", "gym3/LICENSES.md", "glfw/GLFW-3.3.2-LICENSE.md",
                   "qt/LICENSE.LGPL3", "qt/LICENSE.GPL3", "numpy/LGPL-2.1.txt"):
        assert (app / "_internal" / "licenses" / "third_party" / notice).is_file(), notice
    assert not list(app.rglob("*ffmpeg*.exe")), "unused FFmpeg must not be distributed"
    runtime = json.loads((ROOT / ".artifacts/licensed-runtime/manifest.json").read_text(encoding="utf-8"))
    for row in runtime["vc14"]["files"]:
        assert hashlib.sha256((app / "_internal" / row["name"]).read_bytes()).hexdigest() == row["sha256"]
    for binary in app.rglob("*.dll"):
        name = binary.name.lower()
        assert name not in ("msvcr110.dll", "msvcr100.dll", "ucrtbase.dll") and not name.startswith("api-ms-win-")
    environment = {key: value for key, value in os.environ.items()
                   if not key.upper().startswith(("PYTHON", "VIRTUAL_ENV", "CONDA", "PYGLFW", "GLCONTEXT"))}
    environment["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
    environment["LOCALAPPDATA"] = str(extraction / "User data")
    baseline = json.loads((ROOT / ".artifacts" / "upstream-smoke.json").read_text(encoding="utf-8"))
    results = []
    for case in baseline["results"]:
        if not args.all and not (case["game"] in ("coinrun", "caveflyer", "heist") and case["mode"] == "hard"):
            continue
        report_path = extraction / f"case-{len(results)}.json"
        command = [str(exe), "--game", case["game"], "--difficulty", case["mode"],
                   "--vision", case["vision"], "--level-seed", "42",
                   "--verify-engine", str(report_path)]
        if case["simplified"]:
            command += ["--disable-backgrounds", "--restrict-themes", "--monochrome"]
        process = subprocess.Popen(command, cwd=extraction, env=environment, shell=False)
        try:
            code = process.wait(timeout=45)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise RuntimeError(f"Frozen check timed out: {command}. Check startup dialogs and logs.") from None
        if code != 0 or not report_path.is_file():
            raise RuntimeError(f"Frozen check failed ({code}): {command}")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["frozen"] is True and report["gui_verified"] is False
        assert report["viewer_library"]["sha256"] == runtime["glfw"]["sha256"]
        assert report["viewer_library"]["version"] == runtime["glfw"]["version_string"]
        assert report["sha256"] == case["sha256"], f"Output differs from upstream: {case}"
        results.append(report)
        print(f"PASS frozen {case['game']} {case['mode']} {case['vision']} simple={case['simplified']}", flush=True)
    output = dict(
        gui_verified=False, clean_machine_verified=False, stripped_environment=True,
        unicode_path_verified=True, files_matching_upstream=files_checked,
        archive_sha256=hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        archive_bytes=archive_path.stat().st_size, python=sys.version,
        results=results,
    )
    (ROOT / ".artifacts" / "frozen-verification.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(results)} frozen native cases and {files_checked} original data files")


if __name__ == "__main__":
    main()
