"""Copy notices from installed runtime distributions; never fetch at game runtime."""

from __future__ import annotations

import importlib.metadata as metadata
import json
from pathlib import Path
import shutil
import sys

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    destination = ROOT / "third_party"
    destination.mkdir(exist_ok=True)
    pending = ["procgen", "pyinstaller"]
    seen: set[str] = set()
    inventory = []
    while pending:
        name = canonicalize_name(pending.pop())
        if name in seen:
            continue
        seen.add(name)
        distribution = metadata.distribution(name)
        for requirement in distribution.requires or []:
            dependency = Requirement(requirement)
            if dependency.marker is None or dependency.marker.evaluate({"extra": ""}):
                pending.append(dependency.name)
        copied = []
        for file in distribution.files or []:
            if not any(word in file.name.lower() for word in ("license", "copying", "notice", "copyright")):
                continue
            source = Path(distribution.locate_file(file))
            if not source.is_file():
                continue
            # Keep names distinct, including nested dependency license directories.
            relative = Path(*[part for part in file.parts if part not in ("..", ".")])
            target = destination / name / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            copied.append(str(target.relative_to(destination)))
        inventory.append(dict(name=name, version=distribution.version,
                              license=distribution.metadata.get("License-Expression") or distribution.metadata.get("License"),
                              notices=copied))
    python_root = Path(sys.base_prefix)
    for source, target in [
        (python_root / "LICENSE.txt", destination / "python" / "LICENSE.txt"),
        (python_root / "tcl" / "tcl8.6" / "license.terms", destination / "tcl" / "license.terms"),
        (python_root / "tcl" / "tk8.6" / "license.terms", destination / "tk" / "license.terms"),
    ]:
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_file():
            shutil.copyfile(source, target)
        elif not target.is_file():
            raise FileNotFoundError(f"Required runtime notice not found: {source}; supply {target}")
    (destination / "inventory.json").write_text(
        json.dumps(sorted(inventory, key=lambda row: row["name"]), indent=2) + "\n", encoding="utf-8"
    )
    # Flat path retained for users looking for the engine's own license.
    shutil.copyfile(Path(metadata.distribution("procgen").locate_file("procgen-0.10.7.dist-info/LICENSE")),
                    destination / "procgen" / "LICENSE")
    if not (destination / "procgen" / "ASSET_LICENSES.md").is_file():
        raise FileNotFoundError("Fetch upstream 0.10.7 ASSET_LICENSES.md before building.")
    print(f"Collected notices for {len(inventory)} distributions plus Python/Tcl/Tk")


if __name__ == "__main__":
    main()
