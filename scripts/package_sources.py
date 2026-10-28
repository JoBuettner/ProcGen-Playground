"""Create an actual corresponding-source companion for the portable binary."""

from __future__ import annotations

import json
from pathlib import Path
import zipfile

from prepare_license_sources import ROOT, digest, prepare_archives


def relink_inputs() -> list[dict]:
    """Include the verified optional shortcut, never arbitrary build directories."""
    path = ROOT / "docs/licensing/NUMERICAL-RELINK-INPUTS.json"
    if not path.is_file():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))["files"]
    present = [(ROOT / row["local_path"]).is_file() for row in rows]
    # A fresh clone can provide the complete source-only reconstruction route.
    # A partially staged shortcut must not silently produce an incomplete set.
    if not any(present):
        return []
    for row in rows:
        source = (ROOT / row["local_path"]).resolve()
        archive = row["archive_path"]
        if not source.is_relative_to((ROOT / ".artifacts/license-sources/numerical/relink-inputs").resolve()):
            raise ValueError(f"Relink input outside its staging directory: {source}")
        if not archive.startswith("generated/numerical/") or ".." in archive.split("/") or "\\" in archive:
            raise ValueError(f"Unsafe relink archive path: {archive}")
        if source.suffix.lower() in (".exe", ".dll", ".pyd"):
            raise ValueError(f"Compiler/runtime binaries are not source-companion inputs: {source}")
        if not source.is_file() or source.stat().st_size != row["bytes"] or digest(source) != row["sha256"]:
            raise ValueError(f"Missing or altered relink input: {source}")
    return rows


def project_files() -> list[Path]:
    roots = ("src", "scripts", "packaging", "docs", "tests", "third_party", ".github")
    files = [p for folder in roots for p in (ROOT / folder).rglob("*")
             if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")]
    names = ("LICENSE", "README.md", "PROCGEN_PLAYGROUND_CODEX_PLAN.md", "pyproject.toml",
             "requirements-windows.txt", "requirements-windows.lock", "requirements-bootstrap.lock",
             ".gitignore", ".gitattributes")
    return sorted(files + [ROOT / name for name in names])


def main() -> None:
    rows = prepare_archives(download=False)
    objects = relink_inputs()
    portable = ROOT / "dist/ProcGenPlayground-Windows-x64-portable.zip"
    if not portable.is_file():
        raise FileNotFoundError("Package the portable binary before its source companion")
    target = ROOT / "dist/ProcGenPlayground-corresponding-sources.zip"
    prefix = "ProcGenPlayground-sources/"
    manifest = dict(schema=1, binary_archive=portable.name, binary_sha256=digest(portable),
                    source_archives=rows, numerical_relink_inputs=objects, files=[])
    with zipfile.ZipFile(target, "w") as package:
        for path in project_files():
            relative = "project/" + path.relative_to(ROOT).as_posix()
            package.write(path, prefix + relative, compress_type=zipfile.ZIP_DEFLATED)
            manifest["files"].append(dict(path=relative, sha256=digest(path)))
        for row in rows:
            name = "archives/" + row["filename"]
            package.write(ROOT / row["cache_path"], prefix + name, compress_type=zipfile.ZIP_STORED)
            manifest["files"].append(dict(path=name, sha256=row["sha256"]))
        for row in objects:
            package.write(ROOT / row["local_path"], prefix + row["archive_path"], compress_type=zipfile.ZIP_DEFLATED)
            manifest["files"].append(dict(path=row["archive_path"], sha256=row["sha256"]))
        readme = (ROOT / "docs/licensing/SOURCE-COMPANION.md").read_bytes()
        package.writestr(prefix + "README.md", readme, compress_type=zipfile.ZIP_DEFLATED)
        package.writestr(prefix + "manifest.json", json.dumps(manifest, indent=2) + "\n",
                         compress_type=zipfile.ZIP_DEFLATED)
    checksum = digest(target)
    target.with_suffix(".zip.sha256").write_text(f"{checksum}  {target.name}\n", encoding="ascii")
    print(f"Source companion: {target.stat().st_size / 1024**2:.1f} MiB; SHA256 {checksum}")


if __name__ == "__main__":
    main()
