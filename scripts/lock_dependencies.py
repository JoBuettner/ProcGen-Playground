"""Hash previously downloaded artifacts for this Windows/Python build target."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from packaging.utils import canonicalize_name, parse_sdist_filename, parse_wheel_filename

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    artifacts = {}
    for path in (ROOT / "wheelhouse").iterdir():
        if path.suffix == ".whl":
            name, version, _, _ = parse_wheel_filename(path.name)
        else:
            name, version = parse_sdist_filename(path.name)
        key = canonicalize_name(name)
        if key in artifacts:
            raise ValueError(f"Multiple artifacts for {key}; use a fresh wheelhouse")
        artifacts[key] = dict(name=key, version=str(version), filename=path.name,
                              sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    lines = []
    bootstrap = []
    for requirement in (ROOT / "requirements-windows.txt").read_text(encoding="utf-8-sig").splitlines():
        name, version = requirement.split("==")
        row = artifacts[canonicalize_name(name)]
        assert row["version"] == version
        line = f"{name}=={version} --hash=sha256:{row['sha256']}"
        lines.append(line)
        if row["name"] in ("pip", "setuptools", "wheel"):
            bootstrap.append(line)
    header = "# Generated for Windows x64 / CPython 3.10. See docs/BUILD.md.\n"
    (ROOT / "requirements-windows.lock").write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "requirements-bootstrap.lock").write_text(header + "\n".join(bootstrap) + "\n", encoding="utf-8")
    (ROOT / "docs" / "DEPENDENCY_ARTIFACTS.json").write_text(
        json.dumps(sorted(artifacts.values(), key=lambda row: row["name"]), indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
