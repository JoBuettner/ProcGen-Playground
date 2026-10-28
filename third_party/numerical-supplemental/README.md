# Numerical Windows runtime notices

These files supplement NumPy 1.26.4's wheel license. They cover the MinGW-w64,
winpthreads and GCC runtime code statically linked into the wheel's OpenBLAS DLL;
they do not describe an additional application feature or a redistributed
compiler/toolchain. The installed wheel and its DLL have not been modified.

The original DLL has defined COFF code symbols for `__mingw_strtod`,
`__mingw_snprintf`, `__mingw_vfprintf`, `pthread_condattr_destroy`,
`pthread_create`, `__gcc_register_frame` and GCC exception/emulated TLS helpers.
The full local symbol record is
`.artifacts/license-sources/numerical/runtime-symbol-evidence.json`.

`OpenBLAS-x64-source-notices.txt` supplements the wheel's aggregate notice with
48 representative copyright/license comment blocks from the preserved OpenBLAS
runtime source areas, including the University of Texas at Austin BSD notice
used by common headers/x64 kernels and Intel's LAPACKE BSD notices. Equivalent
legal text is deduplicated despite whitespace or trailing per-function metadata;
each representative legal block remains verbatim. Some files in these source
areas are unused by this build; including their notices does not assert they
were all linked. `OPENBLAS-NOTICE-PROVENANCE.json` maps each notice to its source
paths and records hashes. `LAPACK-LICENSE.txt` is the archive's full LAPACK
license. The source archive and reproducible collector
`docs/licensing/numerical-relink/collect-openblas-notices.py` preserve the rest of
the context. The upstream source revision is
`c2f4bdbbb43a1d20a7342f40122e18e573ce436a`.

The complete MinGW-w64 runtime notice is included, rather than guessing which
individual notices may be removed. Its upstream introduction specifically
instructs distributors of binaries built using MinGW-w64 to preserve this file.
It includes the project notice, getopt/NetBSD, gdtoa/David M. Gay/Lucent, Sun
math-library and Wine-header notices. `MinGW-w64-COPYING.txt` preserves the
overall ZPL-2.1 notice; `MinGW-w64-AUTHORS.txt` preserves its referenced author
list. `winpthreads-COPYING.txt` preserves the project's MIT notice and the
Lockless Inc. BSD notice. These notices are copied byte-for-byte from the full
source archive at commit `acc9b9d9eb63a13d8122cbac4882eb5f4ee2f679`.

Primary source paths:

- [MinGW-w64 overall license](https://github.com/mingw-w64/mingw-w64/blob/acc9b9d9eb63a13d8122cbac4882eb5f4ee2f679/COPYING)
- [MinGW-w64 runtime notice](https://github.com/mingw-w64/mingw-w64/blob/acc9b9d9eb63a13d8122cbac4882eb5f4ee2f679/COPYING.MinGW-w64-runtime/COPYING.MinGW-w64-runtime.txt)
- [winpthreads license](https://github.com/mingw-w64/mingw-w64/blob/acc9b9d9eb63a13d8122cbac4882eb5f4ee2f679/mingw-w64-libraries/winpthreads/COPYING)

The portable Rtools 2022-02-06 bundle used to reproduce the wheel's compiler
contains UCRT MinGW-w64 CRT, headers and winpthreads version
`9.0.0.6214.acc9b9d9e-1`. That package metadata and the matching historical
Rtools recipes identify the preserved source revision. The archived Rtools
recipe set also preserves its CRT and winpthreads patches. Its winpthreads
recipe has a later package release number than the installed package; this is
not independent proof that every patch was applied in the historical binary.
The source revision, full upstream notices, and both sets of build materials
are retained without deleting notices based on that uncertainty.

`GCC-COPYING3.txt` and `GCC-RUNTIME-EXCEPTION.txt` come byte-for-byte from GCC
10.3.0's root `COPYING3` and `COPYING.RUNTIME`. They preserve the full terms for
the GCC runtime portions, including libgcc. NumPy's wheel license already
contains the GCC Runtime Library Exception and GPLv3 for libgfortran. This
exception does **not** cover the separately licensed libquadmath; that library's
LGPL-2.1 text is at `third_party/numpy/LGPL-2.1.txt`, and its source/relinking
materials are documented in `docs/licensing/NUMERICAL-SOURCES.md`.

`NOTICE-PROVENANCE.json` records the MinGW-w64/GCC copied files' original paths
and SHA-256 hashes.
The full source archives and patch recipes are listed in
`docs/licensing/NUMERICAL-SOURCE-MANIFEST.json` and must accompany the binary in
the corresponding-source companion. No licensing claim about other Rtools
tools or a redistribution of the whole compiler bundle is made here.
