"""Preserve license headers from the immutable x64 OpenBLAS runtime source."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    prefixes = ("driver/", "interface/", "kernel/generic/", "kernel/x86/",
                "kernel/x86_64/", "lapack/", "lapack-netlib/")
    groups = {}
    with tarfile.open(args.archive) as archive:
        for member in archive:
            if not member.isfile():
                continue
            relative = member.name.split("/", 1)[1]
            if "/" in relative and not relative.startswith(prefixes):
                continue
            if not relative.endswith((".c", ".h", ".S", ".s", ".cpp")):
                continue
            text = archive.extractfile(member).read().decode("utf-8", "replace")
            comments = list(re.finditer(r"/\*.*?\*/", text, re.S))
            for index, match in enumerate(comments):
                block = match.group()
                if not re.search(r"copyright|SPDX-License-Identifier", block, re.I):
                    continue
                # UT Austin's notice uses a separate one-line C comment on
                # every line. Keep that entire run, but not adjacent algorithm
                # documentation, which is not part of the legal notice.
                if "\n" not in block:
                    left = right = index
                    while left > 0 and "\n" not in comments[left - 1].group() and not text[comments[left - 1].end():comments[left].start()].strip():
                        left -= 1
                    while right + 1 < len(comments) and "\n" not in comments[right + 1].group() and not text[comments[right].end():comments[right + 1].start()].strip():
                        right += 1
                    block = text[comments[left].start():comments[right].end()]
                # Intel LAPACKE places per-function Contents/Author metadata
                # after a complete identical legal notice in the same comment.
                # Deduplicate by legal text, retaining the first complete block.
                legal_text = re.split(r"\n\*\s*Contents:", block, maxsplit=1)[0]
                normalized = re.sub(r"/\*|\*/|^\s*\*", "", legal_text, flags=re.M)
                key = re.sub(r"\s+", " ", normalized).strip()
                group = groups.setdefault(key, {"text": block, "source_paths": []})
                group["source_paths"].append(relative)
        license_path = next(m for m in archive.getmembers() if m.name.endswith("/lapack-netlib/LICENSE"))
        lapack_license = archive.extractfile(license_path).read().decode("utf-8")
    args.output.mkdir(parents=True, exist_ok=True)
    record = {"source_archive": args.archive.name,
              "source_archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
              "source_revision": "c2f4bdbbb43a1d20a7342f40122e18e573ce436a",
              "scope": "copyright/license comment blocks in x86/x64 runtime source areas; overinclusive within these areas",
              "groups": []}
    sections = ["OpenBLAS x86/x64 source copyright and license headers\n"
                "Source revision c2f4bdbbb43a1d20a7342f40122e18e573ce436a.\n"
                "Verbatim representative comment blocks; equivalent legal text deduplicated\n"
                "despite whitespace or trailing per-function Contents/Author metadata.\n"
                "The listed source areas include files unused by this particular build;\n"
                "their inclusion is not a claim that every listed file was linked.\n"
                "The full source archive retains all per-file notices.\n"]
    for index, group in enumerate(groups.values(), 1):
        block = group["text"]
        sections.append(f"\n=== Notice {index}; example source: {group['source_paths'][0]} ===\n\n{block}\n")
        record["groups"].append({"notice": index, "sha256": hashlib.sha256(block.encode()).hexdigest(),
                                  "source_paths": group["source_paths"]})
    output = args.output / "OpenBLAS-x64-source-notices.txt"
    output.write_text("".join(sections), encoding="utf-8", newline="\n")
    lapack = args.output / "LAPACK-LICENSE.txt"
    lapack.write_text(lapack_license, encoding="utf-8", newline="\n")
    record["output_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    record["lapack_license_sha256"] = hashlib.sha256(lapack.read_bytes()).hexdigest()
    (args.output / "OPENBLAS-NOTICE-PROVENANCE.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"Preserved {len(groups)} notice groups in {output.stat().st_size} bytes")


if __name__ == "__main__":
    main()
