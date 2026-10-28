"""Verify binary/source pairing, source inclusion, and notice/runtime coverage."""

from __future__ import annotations

import hashlib
import ast
import base64
import importlib.metadata as metadata
import json
from pathlib import Path
import sys
import zipfile

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from prepare_license_sources import ROOT, digest, source_rows
from prepare_windows_runtime import verify_msvc_exports


def verify_source_package(path: Path, binary_sha256: str, rows: list[dict]) -> dict:
    with zipfile.ZipFile(path) as package:
        prefix = "ProcGenPlayground-sources/"
        manifest = json.loads(package.read(prefix + "manifest.json"))
        assert manifest["binary_sha256"] == binary_sha256, "source companion refers to a different binary ZIP"
        assert manifest["source_archives"] == rows, "source manifest differs from pinned inputs"
        files = {item["path"]: item["sha256"] for item in manifest["files"]}
        for row in rows:
            assert files.get("archives/" + row["filename"]) == row["sha256"], "required source archive omitted"
        for row in manifest.get("numerical_relink_inputs", []):
            assert files.get(row["archive_path"]) == row["sha256"], "relink input omitted"
        for name, expected in files.items():
            result = hashlib.sha256()
            with package.open(prefix + name) as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    result.update(block)
            assert result.hexdigest() == expected, name
    return manifest


def wheel_native_inputs() -> dict[Path, dict]:
    locked = {}
    for line in (ROOT / "requirements-windows.lock").read_text().splitlines():
        if line and not line.startswith("#"):
            requirement = Requirement(line.split(" --hash=")[0])
            locked[canonicalize_name(requirement.name)] = next(iter(requirement.specifier)).version
    notices = {row["name"] for row in json.loads((ROOT / "third_party/inventory.json").read_text())}
    owned = {}
    for distribution in metadata.distributions():
        name = canonicalize_name(distribution.metadata["Name"])
        if locked.get(name) != distribution.version or name not in notices:
            continue
        for file in distribution.files or []:
            if file.suffix.lower() in (".dll", ".pyd", ".exe"):
                owned[Path(distribution.locate_file(file)).resolve()] = dict(
                    distribution=name, version=distribution.version,
                    record_hash=file.hash)
    return owned


def verify_wheel_input(source: Path, owned: dict[Path, dict]) -> dict:
    assert source in owned, f"Native file has no locked distribution/notice owner: {source}"
    row = owned[source]
    recorded = row["record_hash"]
    if recorded is not None:
        actual = base64.urlsafe_b64encode(hashlib.new(recorded.mode, source.read_bytes()).digest()).decode().rstrip("=")
        assert actual == recorded.value, f"Wheel RECORD hash mismatch: {source}"
    return dict(distribution=row["distribution"], version=row["version"], record_hash_verified=recorded is not None)


def native_provenance(folder: Path, runtime: dict) -> list[dict]:
    """Resolve every shipped native file to controlled or pinned build inputs."""
    toc = ast.literal_eval((ROOT / "build/procgen-playground/COLLECT-00.toc").read_text(encoding="utf-8"))[0]
    native = []
    recorded = set()
    site = Path(sys.prefix) / "Lib/site-packages"
    owned = wheel_native_inputs()
    controlled = {(ROOT / row["path"]).resolve() for row in [*runtime["vc14"]["files"], runtime["glfw"]]}
    for name, original, kind in toc:
        source = Path(original).resolve()
        if source.suffix.lower() not in (".dll", ".pyd", ".exe"):
            continue
        target = folder / name if kind == "EXECUTABLE" else folder / "_internal" / name
        wheel = None
        if source in controlled:
            origin = "controlled runtime manifest"
        elif source.is_relative_to(site.resolve()):
            wheel = verify_wheel_input(source, owned)
            origin = "pinned installed wheel"
        elif source.is_relative_to(Path(sys.base_prefix).resolve()):
            origin = "CPython 3.10.1 installation"
        elif kind == "EXECUTABLE" and source.parent == (ROOT / "build/procgen-playground").resolve():
            origin = "PyInstaller generated application (bootloader exception)"
        else:
            raise AssertionError(f"Unexpected native input origin: {source}")
        assert digest(target) == digest(source), f"Native build input changed: {name}"
        relative = target.relative_to(folder).as_posix()
        recorded.add(relative)
        native.append(dict(path=relative, source=str(source), origin=origin,
                           wheel=wheel, bytes=target.stat().st_size, sha256=digest(target)))
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob("*")
              if p.is_file() and p.suffix.lower() in (".dll", ".pyd", ".exe")}
    assert actual == recorded, f"Native files missing from provenance: {actual ^ recorded}"
    return native


def main() -> None:
    folder = ROOT / "dist/ProcGenPlayground"
    portable = ROOT / "dist/ProcGenPlayground-Windows-x64-portable.zip"
    sources = ROOT / "dist/ProcGenPlayground-corresponding-sources.zip"
    runtime = json.loads((ROOT / ".artifacts/licensed-runtime/manifest.json").read_text(encoding="utf-8"))
    required = ("THIRD-PARTY-NOTICES.txt", "LICENSE", "README.md",
                "_internal/licenses/third_party/qt/LICENSE.LGPL3",
                "_internal/licenses/third_party/qt/LICENSE.GPL3",
                "_internal/licenses/third_party/qt/attribution-index.json",
                "_internal/licenses/third_party/numpy/LGPL-2.1.txt",
                "_internal/licenses/third_party/gym3/LICENSES.md",
                "_internal/licenses/third_party/procgen/ASSET_LICENSES.md",
                "_internal/licenses/third_party/microsoft/DOWNSTREAM-TERMS.md",
                "_internal/licenses/SOURCE-COMPANION.md")
    with zipfile.ZipFile(portable) as package:
        for name in required:
            assert package.read("ProcGenPlayground/" + name) == (folder / name).read_bytes(), name
        for source in (ROOT / "third_party").rglob("*"):
            if source.is_file():
                name = "_internal/licenses/third_party/" + source.relative_to(ROOT / "third_party").as_posix()
                assert package.read("ProcGenPlayground/" + name) == source.read_bytes(), name
                assert (folder / name).read_bytes() == source.read_bytes(), name
    for archive in (portable, sources):
        assert archive.with_suffix(".zip.sha256").read_text().split()[0] == digest(archive), archive.name
    manifest = verify_source_package(sources, digest(portable), source_rows())
    native = native_provenance(folder, runtime)
    export_check = verify_msvc_exports(folder, runtime["vc14"])
    for row in runtime["vc14"]["files"]:
        assert digest(folder / "_internal" / row["name"]) == row["sha256"]
    assert digest(folder / "_internal/glfw/glfw3.dll") == runtime["glfw"]["sha256"]
    qt_index = json.loads((folder / "_internal/licenses/third_party/qt/attribution-index.json").read_text())
    for entry in qt_index["entries"]:
        if entry["notice"]:
            assert (folder / "_internal/licenses/third_party/qt/source-notices" / entry["notice"]).is_file()
    report = dict(binary_sha256=digest(portable), sources_sha256=digest(sources),
                  source_archives=len(source_rows()), source_files_verified=len(manifest["files"]),
                  numerical_relink_objects=len(manifest.get("numerical_relink_inputs", [])),
                  native_files=native, native_file_count=len(native), export_check=export_check,
                  qt_attribution_entries=len(qt_index["entries"]),
                  controlled_runtime_sha256={r["name"]: r["sha256"] for r in runtime["vc14"]["files"]},
                  glfw_sha256=runtime["glfw"]["sha256"], source_delivery="paired actual archive, no written-offer fallback",
                  desktop_verified=False, separate_pc_verified=False)
    (ROOT / ".artifacts/license-bundle-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"License bundle verified: {report['source_archives']} source archives, {report['source_files_verified']} source files")


if __name__ == "__main__":
    main()
