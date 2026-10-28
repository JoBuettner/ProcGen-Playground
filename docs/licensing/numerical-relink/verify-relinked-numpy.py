"""Verify a disposable relink without changing the installed NumPy/runtime."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pefile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
INSTALLED_SITE = REPO / ".venv" / "Lib" / "site-packages"
DLL_NAME = "libopenblas64__v0.3.23-293-gc2f4bdbb-gcc_10_3_0-2bde3a66a51006b2b53eb373ff767a3f.dll"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exports(path):
    # This library has more names than pefile's default 8192-name safety cap.
    pe = pefile.PE(str(path), max_symbol_exports=65536)
    names = {entry.name.decode("ascii") for entry in pe.DIRECTORY_ENTRY_EXPORT.symbols if entry.name}
    assert len(names) == pe.DIRECTORY_ENTRY_EXPORT.struct.NumberOfNames, "Incomplete PE export parse"
    return names


def worker(site, output):
    sys.path.insert(0, str(site))
    import numpy as np

    assert Path(np.__file__).resolve().is_relative_to(site.resolve()), np.__file__
    dll_path = site / "numpy.libs" / DLL_NAME
    dll = ctypes.CDLL(str(dll_path))
    get_config = dll.openblas_get_config64_
    get_config.restype = ctypes.c_char_p
    rng = np.random.RandomState(42)
    results = {}
    for dtype in (np.float32, np.float64, np.complex64, np.complex128):
        a = rng.randn(48, 48).astype(dtype)
        b = rng.randn(48, 48).astype(dtype)
        if np.issubdtype(dtype, np.complexfloating):
            a += 1j * rng.randn(48, 48).astype(dtype)
            b += 1j * rng.randn(48, 48).astype(dtype)
        name = np.dtype(dtype).name
        results[f"{name}_dot"] = a @ b
        a += np.eye(48, dtype=dtype) * 100
        results[f"{name}_solve"] = np.linalg.solve(a, b)
        u, s, vh = np.linalg.svd(a)
        results[f"{name}_svd_values"] = s
        tolerance = 2e-5 if dtype in (np.float32, np.complex64) else 1e-12
        assert np.allclose(a @ results[f"{name}_solve"], b, rtol=tolerance, atol=tolerance)
        assert np.allclose((u * s) @ vh, a, rtol=tolerance, atol=tolerance)
    np.savez(output, **results)
    record = {"numpy_file": np.__file__, "numpy_version": np.__version__,
              "loaded_dll": str(dll_path), "config": get_config().decode(),
              "cases": list(results), "solve_and_svd_residual_checks": "passed"}
    try:
        probe = dll.procgen_quadmath_relink_probe
    except AttributeError:
        record["modified_libquadmath_probe"] = None
    else:
        probe.restype = ctypes.c_char_p
        record["modified_libquadmath_probe"] = probe().decode()
    Path(str(output) + ".json").write_text(json.dumps(record, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dll", type=Path)
    parser.add_argument("--installed-site", type=Path, default=INSTALLED_SITE,
                        help="Unmodified NumPy 1.26.4 site-packages directory")
    parser.add_argument("--report", default="relink-verification.json")
    parser.add_argument("--probe-required", action="store_true")
    parser.add_argument("--worker-site", type=Path)
    parser.add_argument("--worker-output", type=Path)
    args = parser.parse_args()
    if args.worker_site:
        worker(args.worker_site, args.worker_output)
        return
    assert args.dll and args.dll.exists()
    installed_site = args.installed_site.resolve()
    original = installed_site / "numpy.libs" / DLL_NAME
    before = sha256(original)
    missing = sorted(exports(original) - exports(args.dll))
    assert not missing, f"Missing original exports: {missing}"
    site = ROOT / "replacement-site"
    for name in ("numpy", "numpy.libs"):
        destination = site / name
        if not destination.exists():
            shutil.copytree(installed_site / name, destination)
    # Get the reference results in a fresh process before replacing only the copy.
    report_path = ROOT / args.report
    reference = report_path.with_suffix(".original.npz")
    subprocess.run([sys.executable, str(__file__), "--worker-site", str(installed_site),
                    "--worker-output", str(reference)], check=True)
    replacement = site / "numpy.libs" / DLL_NAME
    shutil.copyfile(args.dll, replacement)
    modified = report_path.with_suffix(".replacement.npz")
    subprocess.run([sys.executable, str(__file__), "--worker-site", str(site),
                    "--worker-output", str(modified)], check=True)
    import numpy as np

    with np.load(reference) as ref, np.load(modified) as actual:
        assert ref.files == actual.files
        comparisons = {}
        for name in ref.files:
            tolerance = 2e-5 if "32" in name or "complex64" in name else 1e-12
            assert np.allclose(ref[name], actual[name], rtol=tolerance, atol=tolerance), name
            comparisons[name] = {"passed": True,
                                 "max_absolute_difference": float(np.max(np.abs(ref[name] - actual[name])))}
    after = sha256(original)
    assert before == after, "Installed original DLL was changed"
    record = {"original_dll_sha256_before": before, "original_dll_sha256_after": after,
              "modified_dll": str(args.dll.resolve()), "modified_dll_sha256": sha256(args.dll),
              "original_export_count": len(exports(original)),
              "modified_export_count": len(exports(args.dll)), "missing_original_exports": missing,
              "original_worker": json.loads(Path(str(reference) + ".json").read_text()),
              "modified_worker": json.loads(Path(str(modified) + ".json").read_text()),
              "comparisons": comparisons}
    if args.probe_required:
        assert record["modified_worker"]["modified_libquadmath_probe"] == "ProcGen libquadmath source modification 2026-10-26"
    report_path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
