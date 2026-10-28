"""Rebuild the unmodified ProcGen native engine with replaceable Qt sources.

This is a developer/relinking tool, never invoked by the game at runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVES = {
    "qtbase-everywhere-src-5.13.2.tar.xz": "26b6b686d66a7ad28eaca349e55e2894e5a735f3831e45f2049e93b1daa92121",
    "procgen-5e1dbf341d291eff40d1f9e0c0a0d5003643aebf.tar.gz": "46630fbfb6efbf8a2910104ace31a99025aad806dd996de0e49daaa7e7f757c8",
    "gym3-2ed9d344ede8bbd96b6280e9fbbbf55861ea33a9.tar.gz": "ad46835a1dd6e15257928de9855eda0dc7e49a47d7a682ccaf6c1ff33e8dd7a0",
}
# Same Windows Qt options as ProcGen's pinned build_qt.py. Build only qtbase,
# the sole submodule selected by that script.
QT_OPTIONS = [
    "-confirm-license", "-static", "-release", "-qtnamespace", "ProcGenQt",
    "-opensource", "-nomake", "examples", "-nomake", "tests", "-nomake", "tools",
    "-no-avx2", "-no-avx512", "-no-pch", "-no-harfbuzz", "-no-openssl",
    "-no-dbus", "-no-opengl", "-no-xcb", "-no-libjpeg", "-no-ico", "-no-gif", "-mp",
]


def extract_archive(archive: Path, destination: Path) -> Path:
    """Extract a pinned source tree without archive path/link escapes."""
    with tarfile.open(archive) as source:
        members = source.getmembers()
        roots = set()
        for member in members:
            if "\\" in member.name or ":" in member.name or ".." in member.name.split("/") or member.name.startswith("/"):
                raise ValueError(f"Unsafe source archive member: {member.name}")
            relative = Path(member.name)
            target = (destination / relative).resolve()
            if not target.is_relative_to(destination.resolve()) or member.issym() or member.islnk():
                raise ValueError(f"Unsafe source archive member: {member.name}")
            if not (member.isfile() or member.isdir()):
                raise ValueError(f"Unsupported source archive member: {member.name}")
            roots.add(relative.parts[0])
        if len(roots) != 1:
            raise ValueError("Source archive must contain a single top-level directory")
        source.extractall(destination, members=members)
    return destination / roots.pop()


def visual_studio_environment(installation: Path) -> dict[str, str]:
    script = installation / "Common7" / "Tools" / "VsDevCmd.bat"
    # cmd.exe needs its own outer quoting; list2cmdline's escaped embedded
    # quotes are not cmd's batch-file quoting syntax.
    command = f'cmd.exe /d /s /c "call "{script}" -arch=x64 -host_arch=x64 >nul && set"'
    result = subprocess.run(command, check=True,
                            capture_output=True, text=True)
    # MSBuild rejects duplicate Windows environment names that differ only in
    # case (for example ONEDRIVE/OneDrive). Canonicalize the complete block.
    environment = {name.upper(): value for name, value in os.environ.items()}
    for line in result.stdout.splitlines():
        if "=" in line and not line.startswith("="):
            name, value = line.split("=", 1)
            environment[name.upper()] = value
    paths = environment.get("PATH", "").split(os.pathsep)
    paths = [p for p in paths if "codex-runtimes" not in p.lower()]
    paths += [str(Path(sys.base_prefix)), str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/usr/bin")]
    environment["PATH"] = os.pathsep.join(paths)
    return environment


def normalize_long_forwarders(source: Path) -> list[str]:
    """Keep Qt's generated include shims usable with MSVC's legacy path limit.

    Only a one-line forwarding include is changed, to the same canonical file;
    Qt implementation sources and public API are not altered.
    """
    changed = []
    for header in (source / "include").rglob("*.h"):
        if len(str(header)) < 180 or header.stat().st_size > 512:
            continue
        text = header.read_text(encoding="utf-8")
        match = re.fullmatch(r'\s*#include "([^"\r\n]+)"\s*', text)
        if match is None:
            continue
        target = header.parent / match.group(1)
        if len(str(target)) < 260:
            continue
        canonical = target.resolve(strict=True)
        if len(str(canonical)) >= 260:
            raise ValueError(f"Qt source path is too long for this compiler; use a shorter work path: {canonical}")
        header.write_text(f'#include "{canonical.as_posix()}"\n', encoding="utf-8")
        changed.append(header.relative_to(source).as_posix())
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archives", type=Path, default=ROOT / ".artifacts/license-sources/qt")
    parser.add_argument("--work", type=Path, default=ROOT / ".artifacts/relink-check")
    parser.add_argument("--visual-studio", type=Path,
                        default=Path("C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools"))
    parser.add_argument("--qt-source", type=Path, help="Use an already extracted, optionally modified Qt source tree")
    parser.add_argument("--qt-built", action="store_true", help="Reuse the Qt build in the work directory")
    args = parser.parse_args()
    work = args.work.resolve()
    if " " in str(work):
        raise ValueError("Qt 5.13's build directory must not contain spaces")
    work.mkdir(parents=True, exist_ok=True)
    sources = work / "sources"
    sources.mkdir(exist_ok=True)
    extracted = {}
    for filename, expected in ARCHIVES.items():
        archive = args.archives / filename
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Source archive hash mismatch: {archive}")
        with tarfile.open(archive) as source:
            directory = sources / Path(source.getmembers()[0].name).parts[0]
        stamp = sources / f".{directory.name}.extracted-sha256"
        if directory.exists():
            if not stamp.is_file() or stamp.read_text(encoding="ascii").strip() != expected:
                raise ValueError(f"Incomplete/unverified extraction at {directory}; choose a new work directory")
        else:
            directory = extract_archive(archive, sources)
            stamp.write_text(expected + "\n", encoding="ascii")
        extracted[filename] = directory
    qt_source = args.qt_source.resolve() if args.qt_source else extracted[next(iter(ARCHIVES))]
    normalized_headers = normalize_long_forwarders(qt_source)
    procgen_source = extracted[next(k for k in ARCHIVES if k.startswith("procgen-"))]
    gym3_source = extracted[next(k for k in ARCHIVES if k.startswith("gym3-"))]
    environment = visual_studio_environment(args.visual_studio)
    cmake = args.visual_studio / "Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe"
    if not cmake.is_file():
        raise FileNotFoundError(f"Install Visual Studio's CMake component or supply its installation: {cmake}")
    nmake = shutil.which("nmake.exe", path=environment["PATH"])
    if nmake is None:
        raise FileNotFoundError("Visual Studio x64 nmake not found")
    commands = []

    def run(command: list[str], directory: Path, name: str) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        commands.append(dict(command=command, cwd=str(directory)))
        print(f"{name}: {directory}", flush=True)
        with (work / f"{name}.log").open("w", encoding="utf-8") as log:
            subprocess.run(command, cwd=directory, env=environment, stdout=log,
                           stderr=subprocess.STDOUT, check=True)

    qt_build = work / "qt-build"
    if not args.qt_built:
        run(["cmd.exe", "/d", "/c", str(qt_source / "configure.bat"),
             "-prefix", str(qt_build), *QT_OPTIONS], qt_build, "qt-configure")
        run([nmake], qt_build, "qt-build")
    engine_build = work / "engine-build"
    run([str(cmake), "-S", str(procgen_source / "procgen"), "-B", str(engine_build),
         "-G", "Visual Studio 16 2019", "-A", "x64",
         f"-DCMAKE_PREFIX_PATH={qt_build / 'lib/cmake/Qt5'}",
         f"-DLIBENV_DIR={gym3_source / 'gym3'}", "-DPROCGEN_PACKAGE=ON"],
        work, "engine-configure")
    run([str(cmake), "--build", str(engine_build), "--config", "RelWithDebInfo", "--parallel", "4"],
        work, "engine-build")
    dll = engine_build / "RelWithDebInfo/env.dll"
    report = dict(commands=commands, source_archive_hashes=ARCHIVES,
                  game_source_patches_applied_by_helper=False,
                  normalized_forwarding_headers=normalized_headers,
                  qt_source_override=bool(args.qt_source), qt_build_reused=args.qt_built,
                  rebuilt_engine=str(dll), sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),
                  compiler=environment.get("VCTOOLSVERSION"), windows_sdk=environment.get("WINDOWSSDKVERSION"),
                  qt_source=str(qt_source))
    (work / "rebuild-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Rebuilt engine: {dll}", flush=True)


if __name__ == "__main__":
    main()
