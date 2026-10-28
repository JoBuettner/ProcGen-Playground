"""Prove a modified Qt library can be relinked and run in a disposable app copy."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import tempfile

from rebuild_procgen_native import ROOT, visual_studio_environment

MARKER = "5.13.2-license-relink-check"


def main() -> None:
    work = ROOT / ".artifacts/relink-check"
    source = work / "sources/qtbase-everywhere-src-5.13.2"
    original_dll = work / "engine-build/RelWithDebInfo/env.dll"
    original_copy = work / "env-before-qt-modification.dll"
    if not original_copy.exists():
        assert MARKER.encode("ascii") not in original_dll.read_bytes(), "save an unmodified baseline first"
        shutil.copyfile(original_dll, original_copy)
    original_hash = hashlib.sha256(original_copy.read_bytes()).hexdigest()
    header = source / "src/corelib/global/qglobal.cpp"
    text = header.read_text(encoding="utf-8")
    replacement = f'return "{MARKER}";'
    if replacement not in text:
        if text.count("return QT_VERSION_STR;") != 1:
            raise ValueError("Unexpected Qt qVersion implementation; do not apply the probe blindly")
        header.write_text(text.replace("return QT_VERSION_STR;", replacement), encoding="utf-8")
    installation = Path("C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools")
    environment = visual_studio_environment(installation)
    nmake = shutil.which("nmake.exe", path=environment["PATH"])
    cmake = installation / "Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe"
    commands = [([nmake], work / "qt-build/src/corelib", "qt-modified-core"),
                ([str(cmake), "--build", str(work / "engine-build"), "--config", "RelWithDebInfo",
                  "--target", "env", "--parallel", "4"], work, "qt-modified-engine")]
    for command, directory, label in commands:
        with (work / f"{label}.log").open("w", encoding="utf-8") as log:
            subprocess.run(command, cwd=directory, env=environment, stdout=log,
                           stderr=subprocess.STDOUT, check=True)
    modified_bytes = original_dll.read_bytes()
    assert MARKER.encode("ascii") in modified_bytes, "modified Qt version code was not linked into env.dll"
    modified_hash = hashlib.sha256(modified_bytes).hexdigest()
    assert original_hash != modified_hash
    disposable = Path(tempfile.mkdtemp(prefix="Qt Relink Pruefung ", dir=ROOT / ".artifacts"))
    app = disposable / "ProcGenPlayground"
    shutil.copytree(ROOT / "dist/ProcGenPlayground", app)
    replaced = app / "_internal/procgen/data/prebuilt/env.dll"
    replaced.write_bytes(modified_bytes)
    process_environment = {k: v for k, v in os.environ.items()
                           if not k.upper().startswith(("PYTHON", "VIRTUAL_ENV", "CONDA", "PYGLFW", "GLCONTEXT"))}
    process_environment["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
    process_environment["LOCALAPPDATA"] = str(disposable / "User data")
    baseline = json.loads((ROOT / ".artifacts/upstream-smoke.json").read_text(encoding="utf-8"))
    cases = [c for c in baseline["results"] if c["game"] in ("coinrun", "heist", "caveflyer") and c["mode"] == "hard"]
    results = []
    for index, case in enumerate(cases):
        report_path = disposable / f"case-{index}.json"
        command = [str(app / "ProcGenPlayground.exe"), "--game", case["game"], "--difficulty", case["mode"],
                   "--vision", case["vision"], "--level-seed", "42", "--verify-engine", str(report_path)]
        if case["simplified"]:
            command += ["--disable-backgrounds", "--restrict-themes", "--monochrome"]
        subprocess.run(command, cwd=disposable, env=process_environment, check=True, timeout=45)
        result = json.loads(report_path.read_text(encoding="utf-8"))
        assert result["sha256"] == case["sha256"], case
        results.append(result)
    report = dict(marker=MARKER, qversion_only_modification=True, modified_engine_sha256=modified_hash,
                  verified_at_utc=datetime.now(timezone.utc).isoformat(),
                  unmodified_rebuild_sha256=original_hash, release_engine_unchanged=True,
                  replacement_path=str(replaced), gui_verified=False, separate_pc_verified=False,
                  source_file="qtbase/src/corelib/global/qglobal.cpp",
                  before="return QT_VERSION_STR;", after=replacement,
                  commands=[dict(command=c, cwd=str(d)) for c, d, _ in commands], results=results)
    output = ROOT / ".artifacts/qt-relink-verification.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Modified Qt relink verified: {len(results)} native cases; release files untouched")


if __name__ == "__main__":
    main()
