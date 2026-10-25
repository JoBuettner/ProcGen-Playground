"""Create the development portable archive and SHA-256 checksum."""

from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    dist = ROOT / "dist"
    folder = dist / "ProcGenPlayground"
    if not (folder / "ProcGenPlayground.exe").is_file():
        raise FileNotFoundError("Build the application first")
    # Readme and wrapper license are also available without browsing _internal.
    for filename in ("README.md", "LICENSE"):
        (folder / filename).write_bytes((ROOT / filename).read_bytes())
    archive_path = dist / "ProcGenPlayground-Windows-x64-portable.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(dist))
    checksum = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    archive_path.with_suffix(".zip.sha256").write_text(
        f"{checksum}  {archive_path.name}\n", encoding="ascii"
    )
    unpacked = sum(path.stat().st_size for path in folder.rglob("*") if path.is_file())
    print(f"ZIP: {archive_path.stat().st_size / 1024**2:.1f} MiB; application: {unpacked / 1024**2:.1f} MiB")
    print(f"SHA256: {checksum}")


if __name__ == "__main__":
    main()
