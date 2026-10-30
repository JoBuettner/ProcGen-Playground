"""Source delivery must reject escapes, altered sources and mismatched binaries."""

import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import zipfile
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_license_sources
import package_sources
from rebuild_procgen_native import extract_archive, visual_studio_environment
from verify_license_bundle import verify_source_package, verify_wheel_input
from prepare_windows_runtime import glfw_toolchain, require_runtime_toolset


@pytest.mark.parametrize("name", ("../escape", "tree/../../escape", "/escape", "C:/escape"))
def test_relink_source_extraction_rejects_path_escape(tmp_path: Path, name: str) -> None:
    archive = tmp_path / "bad.tar"
    with tarfile.open(archive, "w") as package:
        member = tarfile.TarInfo(name)
        member.size = 1
        package.addfile(member, io.BytesIO(b"x"))
    with pytest.raises(ValueError, match="Unsafe"):
        extract_archive(archive, tmp_path / "source")


def test_relink_source_extraction_rejects_link(tmp_path: Path) -> None:
    archive = tmp_path / "bad.tar"
    with tarfile.open(archive, "w") as package:
        member = tarfile.TarInfo("tree/link")
        member.type = tarfile.SYMTYPE
        member.linkname = "../../outside"
        package.addfile(member)
    with pytest.raises(ValueError, match="Unsafe"):
        extract_archive(archive, tmp_path / "source")


def test_relink_source_extraction_preserves_file(tmp_path: Path) -> None:
    archive = tmp_path / "good.tar"
    with tarfile.open(archive, "w") as package:
        member = tarfile.TarInfo("tree/README")
        member.size = 6
        package.addfile(member, io.BytesIO(b"source"))
    tree = extract_archive(archive, tmp_path / "source")
    assert (tree / "README").read_bytes() == b"source"


def test_source_preparation_rejects_altered_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    archive = tmp_path / ".artifacts/license-sources/example.tar"
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b"changed")
    monkeypatch.setattr(prepare_license_sources, "ROOT", tmp_path)
    monkeypatch.setattr(prepare_license_sources, "source_rows", lambda: [dict(
        cache_path=".artifacts/license-sources/example.tar", sha256=hashlib.sha256(b"original").hexdigest(),
        bytes=8, component="example")])
    with pytest.raises(ValueError, match="Pinned source archive mismatch"):
        prepare_license_sources.prepare_archives(download=False)


def test_visual_studio_environment_has_no_case_duplicate_names(monkeypatch: pytest.MonkeyPatch) -> None:
    import rebuild_procgen_native

    monkeypatch.setenv("ONEDRIVE", "before")
    monkeypatch.setattr(rebuild_procgen_native.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(
        stdout="OneDrive=after\nPath=C:\\Windows\\System32;C:\\cache\\codex-runtimes\\unrelated\nVCToolsVersion=14.29\n"))
    environment = visual_studio_environment(Path("C:/VisualStudio"))
    assert len(environment) == len({name.upper() for name in environment})
    assert environment["ONEDRIVE"] == "after"
    assert "codex-runtimes" not in environment["PATH"]


@pytest.mark.parametrize("fault", (None, "wrong-binary", "missing-source", "altered-source"))
def test_source_companion_is_complete_and_tied_to_binary(tmp_path: Path, fault: str | None) -> None:
    archive = tmp_path / "sources.zip"
    content = b"complete pinned sources"
    checksum = hashlib.sha256(content).hexdigest()
    rows = [dict(filename="example.tar", sha256=checksum)]
    manifest = dict(binary_sha256="other" if fault == "wrong-binary" else "binary",
                    source_archives=rows, files=[] if fault == "missing-source" else [
                        dict(path="archives/example.tar", sha256=checksum)])
    with zipfile.ZipFile(archive, "w") as package:
        prefix = "ProcGenPlayground-sources/"
        package.writestr(prefix + "manifest.json", json.dumps(manifest))
        if fault != "missing-source":
            package.writestr(prefix + "archives/example.tar", b"altered" if fault == "altered-source" else content)
    if fault is None:
        assert verify_source_package(archive, "binary", rows) == manifest
    else:
        with pytest.raises(AssertionError):
            verify_source_package(archive, "binary", rows)


@pytest.mark.parametrize("fault", (None, "altered", "partial"))
def test_optional_relink_inputs_are_complete_and_hash_locked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                           fault: str | None) -> None:
    monkeypatch.setattr(package_sources, "ROOT", tmp_path)
    rows = []
    for name in ("objects.a", "exports.def"):
        local = ".artifacts/license-sources/numerical/relink-inputs/" + name
        path = tmp_path / local
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"original")
        rows.append(dict(local_path=local, archive_path="generated/numerical/" + name,
                         bytes=8, sha256=hashlib.sha256(b"original").hexdigest()))
    manifest = tmp_path / "docs/licensing/NUMERICAL-RELINK-INPUTS.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps(dict(files=rows)))
    if fault == "altered":
        (tmp_path / rows[0]["local_path"]).write_bytes(b"modified")
    elif fault == "partial":
        (tmp_path / rows[1]["local_path"]).unlink()
    if fault is None:
        assert package_sources.relink_inputs() == rows
    else:
        with pytest.raises(ValueError, match="Missing or altered"):
            package_sources.relink_inputs()


def test_native_provenance_rejects_unowned_site_packages_dll(tmp_path: Path) -> None:
    source = tmp_path / "Lib/site-packages/untracked/native.dll"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"extra optional native dependency")
    with pytest.raises(AssertionError, match="no locked distribution/notice owner"):
        verify_wheel_input(source, {})


def test_native_provenance_rejects_changed_wheel_record(tmp_path: Path) -> None:
    source = tmp_path / "native.pyd"
    source.write_bytes(b"changed")
    ownership = {source: dict(distribution="example", version="1", record_hash=SimpleNamespace(mode="sha256", value="original"))}
    with pytest.raises(AssertionError, match="Wheel RECORD hash mismatch"):
        verify_wheel_input(source, ownership)


def test_controlled_runtime_rejects_a_newer_dependent_toolset() -> None:
    with pytest.raises(RuntimeError, match=r"older than MSVC linker 14\.52"):
        require_runtime_toolset(Path("future_dependency.pyd"), (14, 52), "14.51.36247.0")


@pytest.mark.parametrize("edition,generator", (("2022/Enterprise", "Visual Studio 17 2022"),
                                             ("2019/BuildTools", "Visual Studio 16 2019")))
def test_glfw_toolchain_supports_hosted_and_local_visual_studio(tmp_path: Path, edition: str,
                                                              generator: str) -> None:
    instance = tmp_path / edition
    cmake = instance / "Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe"
    cmake.parent.mkdir(parents=True)
    cmake.touch()
    tool, selection = glfw_toolchain([instance], generator)
    assert tool == cmake
    assert selection[selection.index("-G") + 1] == generator
    assert selection[selection.index("-T") + 1] == "v142"
    assert f"-DCMAKE_GENERATOR_INSTANCE={instance}" in selection


def test_crt_preparation_does_not_require_community_on_build_worker(tmp_path: Path,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    import prepare_windows_runtime

    monkeypatch.setattr(prepare_windows_runtime, "MICROSOFT_SOURCES", tmp_path / "runtime")
    with pytest.raises(FileNotFoundError, match="Pinned Microsoft runtime package missing"):
        prepare_windows_runtime.stage_crt([tmp_path / "2022/Enterprise"], download=False)
