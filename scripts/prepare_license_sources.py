"""Fetch/verify pinned corresponding source archives and collect Qt notices."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def source_rows() -> list[dict]:
    return json.loads((ROOT / "third_party/source-archives.json").read_text(encoding="utf-8"))["sources"]


def prepare_archives(download: bool) -> list[dict]:
    rows = source_rows()
    for row in rows:
        target = ROOT / row["cache_path"]
        if not target.resolve().is_relative_to((ROOT / ".artifacts/license-sources").resolve()):
            raise ValueError(f"Source cache path outside its workspace: {target}")
        if not target.is_file():
            if not download:
                raise FileNotFoundError(f"Missing {target}; run prepare_license_sources.py --download")
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".partial")
            with urllib.request.urlopen(row["url"], timeout=120) as response, temporary.open("wb") as stream:
                while block := response.read(1024 * 1024):
                    stream.write(block)
            if digest(temporary) != row["sha256"]:
                raise ValueError(f"Downloaded source hash mismatch: {target.name}")
            temporary.replace(target)
        if digest(target) != row["sha256"] or target.stat().st_size != row["bytes"]:
            raise ValueError(f"Pinned source archive mismatch: {target}")
        print(f"Verified source {row['component']}: {target.name}", flush=True)
    return rows


def collect_qt_notices(archive: Path) -> None:
    destination = ROOT / "third_party/qt/source-notices"
    manifests = []
    copied: set[str] = set()
    # A sequential compressed-tar pass avoids repeatedly decompressing Qt's
    # entire source tree while copying small individual notice files.
    with tarfile.open(archive, "r|xz") as package:
        for member in package:
            if not member.isfile():
                continue
            parts = member.name.split("/")
            relative = "/".join(parts[1:])
            filename = parts[-1].lower()
            if not ("license" in filename or "licence" in filename or "copying" in filename or
                    filename in ("qt_attribution.json", "ftl.txt")):
                continue
            if ".." in parts or "\\" in member.name or ":" in member.name or member.name.startswith("/"):
                raise ValueError(f"Unsafe Qt notice path: {member.name}")
            content = package.extractfile(member).read()
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            copied.add(relative)
            if filename == "qt_attribution.json":
                items = json.loads(content.decode("utf-8-sig"), strict=False)
                for item in items if isinstance(items, list) else [items]:
                    manifests.append((relative, item))
    entries = []
    for relative, item in manifests:
        license_file = item.get("LicenseFile")
        notice = None
        if license_file:
            notice = posixpath.normpath(posixpath.join(posixpath.dirname(relative), license_file))
            if notice not in copied:
                raise FileNotFoundError(f"Qt attribution references an uncollected license: {relative}: {notice}")
        entries.append(dict(id=item.get("Id"), name=item["Name"], version=item.get("Version"),
                            license=item.get("LicenseId") or item.get("License"),
                            copyright=item.get("Copyright"), attribution=relative, notice=notice,
                            usage=item.get("QtUsage")))
    index = dict(qt_version="5.13.2", scope="conservative full qtbase source attribution superset",
                 source_archive_sha256=digest(archive), notice_file_count=len(copied), entries=entries)
    (ROOT / "third_party/qt/attribution-index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    lines = ["# Qt 5.13.2 third-party attributions", "",
             "Conservative full qtbase attribution superset. ProcGen links Qt Core/Gui;",
             "entries for other platforms and optional modules are retained for completeness.",
             "The original attribution records and license texts are preserved under source-notices/.",
             "Choose the permissive FreeType License (FTL) where FreeType offers FTL or GPL.", ""]
    for entry in entries:
        lines += [f"## {entry['name']}", "", f"License: {entry['license']}", "",
                  entry["copyright"] or "See original attribution record.", ""]
        if entry["notice"]:
            lines += [f"License text: [original notice](source-notices/{entry['notice']})", ""]
    (ROOT / "third_party/qt/ATTRIBUTIONS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Collected {len(copied)} Qt notice/manifests covering {len(entries)} attribution entries")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="allow build-time fetching of missing archives")
    args = parser.parse_args()
    rows = prepare_archives(args.download)
    qt = next(row for row in rows if row["component"] == "Qt 5.13.2")
    collect_qt_notices(ROOT / qt["cache_path"])


if __name__ == "__main__":
    main()
