from pathlib import Path
import hashlib
import json
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, copy_metadata

root = Path(SPECPATH).parent
runtime = json.loads((root / ".artifacts/licensed-runtime/manifest.json").read_text(encoding="utf-8"))
# Native dependency discovery must not pick DLLs from unrelated tools on PATH.
system_root = Path(os.environ["SystemRoot"])
os.environ["PATH"] = os.pathsep.join(map(str, (Path(sys.base_prefix), Path(sys.base_prefix) / "DLLs",
                                              system_root / "System32", system_root)))
datas = []
binaries = []
hiddenimports = ["_cffi_backend", "glcontext.wgl", "moderngl.mgl"]
# ProcGen resolves native/assets relative to its package. gym3 loads font.bin;
# GLFW and ModernGL select their native backend dynamically.
for package in ("procgen", "gym3", "glfw", "moderngl", "glcontext"):
    datas += collect_data_files(package)
    binaries += collect_dynamic_libs(package)
# Select the controlled CRT family and same-version rebuilt viewer. No runtime
# binaries are sourced from the developer's ambient caches.
replacements = {row["name"].lower(): row for row in runtime["vc14"]["files"]}
replacements["glfw3.dll"] = runtime["glfw"]

def controlled_or_system_runtime(path):
    name = Path(path).name.lower()
    return name in (*replacements, "msvcr110.dll", "msvcr100.dll", "ucrtbase.dll") or name.startswith("api-ms-win-")

for row in replacements.values():
    if hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() != row["sha256"]:
        raise ValueError(f"Controlled runtime hash mismatch: {row['path']}")
binaries = [(source, target) for source, target in binaries
            if not controlled_or_system_runtime(source)]
binaries += [(str(root / row["path"]), "." if name != "glfw3.dll" else "glfw")
             for name, row in replacements.items()]
datas += copy_metadata("procgen")
datas += [(str(root / "LICENSE"), "."), (str(root / "README.md"), ".")]
datas += [(str(root / "docs" / "ATTRIBUTION.md"), "licenses")]
datas += [(str(root / "docs" / "LICENSE-AUDIT.md"), "licenses")]
datas += [(str(root / "docs/licensing/SOURCE-COMPANION.md"), "licenses")]
datas += [(str(root / "docs/licensing/REDISTRIBUTION.md"), "licenses")]
datas += [(str(root / "third_party"), "licenses/third_party")]

a = Analysis(
    [str(root / "packaging" / "entry.py")],
    pathex=[str(root / "src")],
    binaries=binaries, datas=datas, hiddenimports=hiddenimports,
    # Runtime uses CFFI's ABI mode only. Build tools and package tests are not
    # needed; excluding setuptools also avoids its vendored runtime hooks.
    # Video recording is not exposed. ImageIO's plugin hook otherwise bundles
    # a GPL-enabled FFmpeg executable that the application never uses.
    excludes=["pytest", "mypy", "setuptools", "pkg_resources", "imageio_ffmpeg"],
    runtime_hooks=[str(root / "packaging/runtime_glfw.py")],
    noarchive=False,
)
# PyInstaller may discover the installed wheel's obsolete runtime or duplicate
# CRTs during dependency expansion. Replace its final TOC too. UCRT/API sets
# are supplied by our minimum supported OS, Windows 10, and are not bundled.
a.binaries = [(name, source, kind) for name, source, kind in a.binaries
              if not controlled_or_system_runtime(name)]
a.datas = [(name, source, kind) for name, source, kind in a.datas
           if not controlled_or_system_runtime(name)]
a.binaries += [("glfw/glfw3.dll" if name == "glfw3.dll" else name,
                str(root / row["path"]), "BINARY") for name, row in replacements.items()]
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="ProcGenPlayground", debug=False, strip=False, upx=False, console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="ProcGenPlayground")
