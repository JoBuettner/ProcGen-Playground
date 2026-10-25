from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, copy_metadata

root = Path(SPECPATH).parent
datas = []
binaries = []
hiddenimports = ["_cffi_backend", "glcontext.wgl", "moderngl.mgl"]
# ProcGen resolves native/assets relative to its package. gym3 loads font.bin;
# GLFW and ModernGL select their native backend dynamically.
for package in ("procgen", "gym3", "glfw", "moderngl", "glcontext"):
    datas += collect_data_files(package)
    binaries += collect_dynamic_libs(package)
datas += copy_metadata("procgen")
datas += [(str(root / "LICENSE"), "."), (str(root / "README.md"), ".")]
datas += [(str(root / "docs" / "ATTRIBUTION.md"), "licenses")]
datas += [(str(root / "third_party"), "licenses/third_party")]

a = Analysis(
    [str(root / "packaging" / "entry.py")],
    pathex=[str(root / "src")],
    binaries=binaries, datas=datas, hiddenimports=hiddenimports,
    # Runtime uses CFFI's ABI mode only. Build tools and package tests are not
    # needed; excluding setuptools also avoids its vendored runtime hooks.
    excludes=["pytest", "mypy", "setuptools", "pkg_resources"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="ProcGenPlayground", debug=False, strip=False, upx=False, console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="ProcGenPlayground")
