"""Extract a pinned official VC14 runtime and build exact GLFW 3.3.2 for VC142.

Build-time operation only: no installer is run and no system location or
installed wheel is modified. See docs/licensing/MICROSOFT-RUNTIME.md.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

import pefile

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / ".artifacts" / "licensed-runtime"
SOURCES = ROOT / ".artifacts" / "license-sources" / "glfw"
GLFW_URL = "https://codeload.github.com/glfw/glfw/zip/refs/tags/3.3.2"
GLFW_SHA256 = "33c6bfc422ca7002befbb39a7a60dc101d32c930ee58be532ffbcd52e9635812"
GLFW_COMMIT = "76dfe13e4ee7c739156260053bc40c938679c754"
MICROSOFT_SOURCES = ROOT / ".artifacts" / "license-sources" / "microsoft"
CRT_VERSION = "14.51.36247.0"
CRT_URL = ("https://download.visualstudio.microsoft.com/download/pr/"
           "ebdab8e5-1d7b-4d9f-a11b-cbb1720c3b12/"
           "843068991DAAA1F73AD9F6239BCE4D0F6A07A51F18C37EA2A867E9BECA71295C/VC_redist.x64.exe")
CRT_PACKAGE_SHA256 = "843068991daaa1f73ad9f6239bce4d0f6a07a51f18c37ea2a867e9beca71295c"
CRT_NAMES = ("msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll")
CRT_SHA256 = {
    "msvcp140.dll": "7c26614e1d733892c2deac7e245ce115504b1d80592dd0a01b08e3e5a55f89ca",
    "vcruntime140.dll": "d1f4225df2cd877dbf130d5668a021dce3f94118455ff5ec952061c30afc9ce7",
    "vcruntime140_1.dll": "a7146c08f89fe5b04541ab507cdb59ff7b44534d4ba3c668a426c6450a03434e",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def installed_visual_studio(version_range: str) -> list[Path]:
    installer = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"))
    vswhere = installer / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    if not vswhere.is_file():
        raise FileNotFoundError("Visual Studio/vswhere is required; see the runtime build notes.")
    output = subprocess.run(
        [str(vswhere), "-version", version_range, "-all", "-products", "*", "-format", "json", "-utf8"],
        check=True, capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    return [Path(item["installationPath"]) for item in json.loads(output.stdout)
            if item.get("isComplete")]


def inspect_signatures(paths: list[Path]) -> list[dict]:
    # Send paths as JSON data, never interpolate them into shell source.
    command = r"""
        $ErrorActionPreference = 'Stop'
        $env:PSModulePath = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\Modules'
        [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
        $paths = [Console]::In.ReadToEnd() | ConvertFrom-Json
        $rows = foreach ($path in $paths) {
            $signature = Get-AuthenticodeSignature -LiteralPath $path
            $item = Get-Item -LiteralPath $path
            [PSCustomObject]@{
                path = $path; status = [string]$signature.Status
                signer = $signature.SignerCertificate.Subject
                version = $item.VersionInfo.FileVersion
            }
        }
        @($rows) | ConvertTo-Json -Depth 4 -Compress
    """
    powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    completed = subprocess.run(
        [str(powershell), "-NoProfile", "-NonInteractive", "-Command", command],
        input=json.dumps([str(path) for path in paths]), capture_output=True,
        encoding="utf-8", timeout=60,
    )
    if completed.returncode:
        raise RuntimeError(f"Signature inspection failed: {completed.stderr}")
    result = json.loads(completed.stdout.lstrip("\ufeff"))
    if isinstance(result, dict):
        result = [result]
    for row in result:
        if row["status"] != "Valid" or "Microsoft Corporation" not in row["signer"]:
            raise RuntimeError(f"Microsoft signature verification failed: {row}")
    return result


def version(path: Path, *, require_x64: bool = True) -> str:
    with pefile.PE(str(path), fast_load=True) as image:
        image.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
        fixed = image.VS_FIXEDFILEINFO[0]
        parts = (fixed.FileVersionMS >> 16, fixed.FileVersionMS & 65535,
                 fixed.FileVersionLS >> 16, fixed.FileVersionLS & 65535)
        if require_x64 and image.FILE_HEADER.Machine != 0x8664:
            raise RuntimeError(f"Expected x64 runtime: {path}")
        return ".".join(map(str, parts))


def imports(path: Path) -> list[str]:
    with pefile.PE(str(path), fast_load=True) as image:
        image.parse_data_directories(directories=[1, 13])
        return sorted({entry.dll.decode("ascii").lower()
                       for directory in ("DIRECTORY_ENTRY_IMPORT", "DIRECTORY_ENTRY_DELAY_IMPORT")
                       for entry in getattr(image, directory, [])})


def expand_cabinet(cabinet: Path, destination: Path) -> None:
    """Extract flat, validated CAB members using the Windows data-extraction utility."""
    content = cabinet.read_bytes()
    # Signed cabinets may have a trailing certificate beyond cbCabinet.
    if (len(content) < 36 or content[:4] != b"MSCF"
            or not 36 <= struct.unpack_from("<I", content, 8)[0] <= len(content)):
        raise RuntimeError(f"Invalid cabinet: {cabinet}")
    position = struct.unpack_from("<I", content, 16)[0]
    for _ in range(struct.unpack_from("<H", content, 28)[0]):
        start = position + 16  # Fixed CFFILE entry followed by its NUL-terminated filename.
        end = content.index(b"\0", start)
        name = content[start:end].decode("ascii")
        if not name or name in (".", "..") or any(char in name for char in "/\\:"):
            raise RuntimeError(f"Unsafe cabinet member: {name}")
        position = end + 1
    destination.mkdir(parents=True, exist_ok=True)
    expand = Path(os.environ["SystemRoot"]) / "System32/expand.exe"
    subprocess.run([str(expand), "-F:*", str(cabinet), str(destination)], check=True,
                   capture_output=True, timeout=60)


def extract_runtime_package(package: Path) -> tuple[Path, dict]:
    """Read the pinned Burn v2 bundle as data; never execute its EXE or MSIs."""
    content = package.read_bytes()
    with pefile.PE(data=content, fast_load=True) as image:
        section = next(item for item in image.sections if item.Name.rstrip(b"\0") == b".wixburn")
        header = section.get_data()
    magic, bundle_version = struct.unpack_from("<II", header)
    count = struct.unpack_from("<I", header, 44)[0]
    if (magic, bundle_version, count) != (0x00F14300, 2, 2):
        raise RuntimeError("Unexpected pinned Microsoft bundle container layout")
    stub_size = struct.unpack_from("<I", header, 24)[0]
    signature_offset, signature_size = struct.unpack_from("<II", header, 32)
    sizes = struct.unpack_from("<II", header, 48)
    offsets = (stub_size, signature_offset + signature_size)
    cabinet_dir = MICROSOFT_SOURCES / "cabinets"
    cabinet_dir.mkdir(parents=True, exist_ok=True)
    cabinets = []
    for index, (offset, size) in enumerate(zip(offsets, sizes)):
        if offset < stub_size or offset + size > len(content):
            raise RuntimeError("Microsoft cabinet extends beyond pinned bundle")
        cabinet = cabinet_dir / f"container-{index}.cab"
        cabinet.write_bytes(content[offset:offset + size])
        cabinets.append(cabinet)
    ux = MICROSOFT_SOURCES / "ux"
    payload = MICROSOFT_SOURCES / "payload"
    expand_cabinet(cabinets[0], ux)
    expand_cabinet(cabinets[1], payload)
    manifest = ET.parse(ux / "0").getroot()
    payload_name = "packages/vcRuntimeMinimum_amd64/cab1.cab"
    row = next(item for item in manifest if item.tag.endswith("}Payload")
               and item.attrib.get("FilePath", "").replace("\\", "/") == payload_name)
    source_name = row.attrib["SourcePath"]
    if source_name != Path(source_name).name or any(char in source_name for char in "/\\:"):
        raise RuntimeError("Unsafe Microsoft payload mapping")
    crt_cabinet = payload / source_name
    if (crt_cabinet.stat().st_size != int(row.attrib["FileSize"])
            or hashlib.sha1(crt_cabinet.read_bytes()).hexdigest().lower() != row.attrib["Hash"].lower()):
        raise RuntimeError("Microsoft bundle payload hash mismatch")
    extracted = MICROSOFT_SOURCES / "crt-x64"
    expand_cabinet(crt_cabinet, extracted)
    return extracted, dict(method="Burn containers parsed as data; Windows expand.exe; no EXE/MSI execution",
                           payload=payload_name, cabinet_sha256=sha256(crt_cabinet),
                           cabinets=[dict(path=relative(path), sha256=sha256(path)) for path in cabinets])


def is_msvc14_runtime(name: str) -> bool:
    return name.endswith(".dll") and name.startswith(
        ("msvcp140", "vcruntime140", "concrt140", "vcomp140", "vcamp140", "vccorlib140"))


def stage_crt(instances: list[Path], download: bool) -> dict:
    # The project's redistribution terms/entitlement do not depend on the IDE
    # edition physically installed on each build worker. Hosted images use
    # Enterprise; extract the same pinned official CRT on both build platforms.
    MICROSOFT_SOURCES.mkdir(parents=True, exist_ok=True)
    package = MICROSOFT_SOURCES / "VC_redist.x64.exe"
    if not package.is_file():
        if not download:
            raise FileNotFoundError("Pinned Microsoft runtime package missing; rerun with --download")
        urllib.request.urlretrieve(CRT_URL, package)
    # The bootstrapper can be x86 even though its selected payload is x64.
    if sha256(package) != CRT_PACKAGE_SHA256 or version(package, require_x64=False) != CRT_VERSION:
        raise RuntimeError("Pinned official Microsoft runtime package version/SHA-256 mismatch")
    package_signature = inspect_signatures([package.resolve()])[0]
    source, extraction = extract_runtime_package(package)
    # Follow the selected libraries' own normal and delay imports, not just the app's seeds.
    selected = set(CRT_NAMES)
    pending = list(CRT_NAMES)
    while pending:
        name = pending.pop()
        for dependency in imports(source / (name + "_amd64")):
            if is_msvc14_runtime(dependency) and dependency not in selected:
                if dependency not in CRT_SHA256:
                    raise RuntimeError(f"New runtime dependency needs a pinned hash: {dependency}")
                selected.add(dependency)
                pending.append(dependency)
    destination = STAGE / "vc14"
    destination.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in sorted(selected):
        original = source / (name + "_amd64")
        file_version = version(original)
        if file_version != CRT_VERSION:
            raise RuntimeError(f"Unexpected runtime family/version: {original}: {file_version}")
        if sha256(original) != CRT_SHA256[name]:
            raise RuntimeError(f"Locked Microsoft runtime SHA-256 mismatch: {original}")
        target = destination / name
        shutil.copyfile(original, target)
        rows.append(dict(name=target.name, path=relative(target), sha256=sha256(target),
                         version=file_version, imports=imports(target)))
    for row, signature in zip(rows, inspect_signatures([(ROOT / row["path"]).resolve() for row in rows])):
        row["signature"] = signature
    return dict(source_kind="official stable VC14 redistributable download, app-local extraction",
                source_package=dict(url=CRT_URL, path=relative(package), sha256=CRT_PACKAGE_SHA256,
                                    signature=package_signature), extraction=extraction,
                version=CRT_VERSION, files=rows, dependency_closure=sorted(selected),
                build_installations=[str(path) for path in instances],
                eligibility="MIT open-source project; Community2022 section1(b)(i); distribution section4",
                redist_list="https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution",
                license="third_party/microsoft/VS-Community-2022-EULA.docx")


def glfw_toolchain(instances: list[Path], generator: str) -> tuple[Path, list[str]]:
    for instance in instances:
        cmake = instance / "Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe"
        if cmake.is_file():
            return cmake, ["-G", generator, "-A", "x64", "-T", "v142",
                           f"-DCMAKE_GENERATOR_INSTANCE={instance}", "-DCMAKE_SYSTEM_VERSION=10.0.19041.0"]
    raise FileNotFoundError("Visual Studio 2022 or 2019 with CMake, v142 and SDK 10.0.19041.0 is required")


def build_glfw(instances: list[Path], download: bool, *, rebuild: bool = False,
               generator: str = "Visual Studio 16 2019") -> dict:
    manifest = STAGE / "manifest.json"
    if manifest.is_file() and not rebuild:
        previous = json.loads(manifest.read_text(encoding="utf-8"))["glfw"]
        records = [previous, previous["source"], previous["toolchain"]["compiler_configuration"],
                   *previous["logs"]]
        if (previous["source"]["sha256"] != GLFW_SHA256
                or previous["source"]["commit"] != GLFW_COMMIT
                or any(not (ROOT / row["path"]).is_file()
                       or sha256(ROOT / row["path"]) != row["sha256"] for row in records)):
            raise RuntimeError("Cached GLFW provenance changed; use --rebuild-glfw to rebuild explicitly")
        return previous
    SOURCES.mkdir(parents=True, exist_ok=True)
    archive = SOURCES / "glfw-3.3.2.zip"
    if not archive.is_file():
        if not download:
            raise FileNotFoundError("GLFW source archive missing; rerun with --download for build-time fetching.")
        urllib.request.urlretrieve(GLFW_URL, archive)
    if sha256(archive) != GLFW_SHA256:
        raise RuntimeError("Pinned GLFW source archive SHA-256 mismatch")
    source_parent = SOURCES / "source"
    source_parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as package:
        for entry in package.infolist():
            target = (source_parent / entry.filename).resolve()
            if not target.is_relative_to(source_parent.resolve()):
                raise RuntimeError("Unexpected source archive path")
        package.extractall(source_parent)
    source = source_parent / "glfw-3.3.2"
    tool, selection = glfw_toolchain(instances, generator)
    # Separate build trees avoid mixing CMake generators on machines with both IDEs.
    build = SOURCES / f"build-vc142-vs{generator.split()[-1]}"
    commands = [
        [str(tool), "-S", str(source), "-B", str(build), *selection,
         "-DBUILD_SHARED_LIBS=ON", "-DUSE_MSVC_RUNTIME_LIBRARY_DLL=ON",
         "-DGLFW_BUILD_EXAMPLES=OFF", "-DGLFW_BUILD_TESTS=OFF", "-DGLFW_BUILD_DOCS=OFF", "-DGLFW_INSTALL=OFF"],
        [str(tool), "--build", str(build), "--config", "Release", "--target", "glfw", "--parallel", "2"],
    ]
    logs = []
    for label, command in zip(("configure", "build"), commands):
        path = SOURCES / f"{label}.log"
        with path.open("w", encoding="utf-8") as stream:
            subprocess.run(command, check=True, stdout=stream, stderr=subprocess.STDOUT, timeout=300)
        logs.append(dict(path=relative(path), sha256=sha256(path)))
    project = (build / "src/glfw.vcxproj").read_text(encoding="utf-8-sig")
    if "<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>" not in project:
        raise RuntimeError("GLFW release build must use /MD")
    target = STAGE / "glfw" / "glfw3.dll"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(build / "src/Release/glfw3.dll", target)
    dependencies = imports(target)
    if "msvcr110.dll" in dependencies:
        raise RuntimeError("Rebuilt GLFW still imports VC11")
    # A finite API inspection, not an OpenGL/desktop behavior test.
    library = ctypes.CDLL(str(target))
    library.glfwGetVersionString.restype = ctypes.c_char_p
    version_string = library.glfwGetVersionString().decode("ascii")
    for feature in ("3.3.2", "Win32", "WGL", "EGL", "OSMesa", "DLL"):
        if feature not in version_string:
            raise RuntimeError(f"Missing original Win32 viewer feature {feature}: {version_string}")
    with pefile.PE(str(target), fast_load=True) as image:
        assert image.FILE_HEADER.Machine == 0x8664
    compiler_record = next(build.glob("CMakeFiles/*/CMakeCCompiler.cmake"))
    return dict(path=relative(target), sha256=sha256(target), imports=dependencies,
                version_string=version_string, signed=False, source_modified=False,
                source=dict(url=GLFW_URL, commit=GLFW_COMMIT, path=relative(archive), sha256=GLFW_SHA256),
                toolchain=dict(cmake_path=str(tool), cmake_sha256=sha256(tool),
                               compiler_configuration=dict(path=relative(compiler_record),
                                                           sha256=sha256(compiler_record)),
                               generator=generator, platform_toolset="v142",
                               windows_sdk="10.0.19041.0", configuration="Release x64 /MD"),
                commands=commands, logs=logs, license="third_party/glfw/GLFW-3.3.2-LICENSE.md")


def require_runtime_toolset(path: Path, linker: tuple[int, int], runtime_version: str) -> None:
    """The PE linker version is an observable minimum, not full compiler provenance."""
    runtime_toolset = tuple(int(part) for part in runtime_version.split(".")[:2])
    if linker > runtime_toolset:
        raise RuntimeError(f"Controlled runtime {runtime_version} is older than MSVC linker "
                           f"{linker[0]}.{linker[1]} required by {path}")


def verify_msvc_exports(bundle: Path, runtime: dict) -> dict:
    if not bundle.is_dir():
        raise FileNotFoundError(f"Native bundle directory does not exist: {bundle}")
    exports = {}
    for row in runtime["files"]:
        if version(ROOT / row["path"]) != runtime["version"]:
            raise RuntimeError(f"Controlled runtime version mismatch: {row['path']}")
        with pefile.PE(str(ROOT / row["path"])) as image:
            exports[row["name"]] = {symbol.name if symbol.name is not None else symbol.ordinal
                                    for symbol in image.DIRECTORY_ENTRY_EXPORT.symbols}
    required = set()
    toolsets = []
    checked = 0
    for path in sorted(bundle.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".exe", ".dll", ".pyd"):
            continue
        with pefile.PE(str(path), fast_load=True) as image:
            image.parse_data_directories(directories=[1, 13])
            uses_runtime = False
            for directory in ("DIRECTORY_ENTRY_IMPORT", "DIRECTORY_ENTRY_DELAY_IMPORT"):
                for entry in getattr(image, directory, []):
                    name = entry.dll.decode("ascii").lower()
                    if is_msvc14_runtime(name) and name not in exports:
                        raise RuntimeError(f"Uncontrolled Microsoft runtime import {path}: {name}")
                    if name not in exports:
                        continue
                    uses_runtime = True
                    required.add(name)
                    for item in entry.imports:
                        symbol = item.name if item.name is not None else item.ordinal
                        if symbol not in exports[name]:
                            raise RuntimeError(f"Controlled runtime lacks import {path}: {name}: {symbol}")
            if uses_runtime:
                linker = (image.OPTIONAL_HEADER.MajorLinkerVersion, image.OPTIONAL_HEADER.MinorLinkerVersion)
                require_runtime_toolset(path, linker, runtime["version"])
                toolsets.append(dict(path=path.relative_to(bundle).as_posix(),
                                     linker_version=".".join(map(str, linker))))
            checked += 1
    if not checked:
        raise RuntimeError(f"No native files found in bundle: {bundle}")
    # Staged runtime dependencies must themselves resolve inside the same controlled family.
    for row in runtime["files"]:
        for name in imports(ROOT / row["path"]):
            if is_msvc14_runtime(name) and name not in exports:
                raise RuntimeError(f"Controlled runtime dependency is missing: {row['name']}: {name}")
    return dict(files_checked=checked, msvc14_imports=sorted(required), missing_exports=[],
                runtime_version=runtime["version"], toolset_checks=toolsets)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="fetch pinned runtime/GLFW sources if absent")
    parser.add_argument("--rebuild-glfw", action="store_true", help="rebuild even if a hash-verified GLFW build exists")
    parser.add_argument("--check-bundle", type=Path, help="check native imports against the controlled CRT exports")
    args = parser.parse_args()
    if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
        raise RuntimeError("This source preparation requires Windows x64 and Visual Studio C++ tools")
    instances = installed_visual_studio("[17.0,18.0)")
    generator = "Visual Studio 17 2022"
    try:
        glfw_toolchain(instances, generator)
    except FileNotFoundError:
        instances = installed_visual_studio("[16.0,17.0)")
        generator = "Visual Studio 16 2019"
    STAGE.mkdir(parents=True, exist_ok=True)
    runtime = stage_crt(instances, args.download)
    glfw = build_glfw(instances, args.download, rebuild=args.rebuild_glfw, generator=generator)
    report = dict(schema=1, minimum_windows="Windows 10 x64", vc14=runtime, glfw=glfw,
                  omit_bundled=("api-ms-win-*.dll", "ucrtbase.dll", "msvcr110.dll", "msvcr100.dll"),
                  redistribution_terms="third_party/microsoft/DOWNSTREAM-TERMS.md")
    if args.check_bundle:
        report["export_check"] = verify_msvc_exports(args.check_bundle.resolve(), runtime)
    manifest = STAGE / "manifest.json"
    manifest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(runtime['files'])} controlled CRT files and GLFW {glfw['version_string']}")
    print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()
