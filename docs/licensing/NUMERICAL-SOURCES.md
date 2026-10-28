# Numerical dependency source and relinking record

Research begun: 2026-10-26; verification completed: 2026-10-28.
Scope: the **unmodified NumPy 1.26.4 CPython 3.10
Windows x64 wheel** used by ProcGen Playground. This is a technical provenance
and build record, not legal clearance. The release must include the actual
source archives and relinking materials described here, rather than relying
only on external links.

## Identified shipped library

The installed wheel contains
`numpy.libs/libopenblas64__v0.3.23-293-gc2f4bdbb-gcc_10_3_0-2bde3a66a51006b2b53eb373ff767a3f.dll`.
Its SHA-256, size, PE timestamp and COFF symbol evidence are recorded in
`NUMERICAL-SOURCE-MANIFEST.json`. Its PE timestamp is **2023-09-28 13:43:57 UTC**.
Calling its exported `openblas_get_config64_` reports
`OpenBLAS 0.3.23.dev USE64BITINT DYNAMIC_ARCH NO_AFFINITY Zen MAX_THREADS=24`.
This identifies the selected runtime core on this host, not a requirement that
all users have a Zen CPU. Local evidence:
`.artifacts/license-sources/numerical/original-dll-evidence.json`.

This DLL really includes libquadmath code: COFF symbols such as
`quadmath_snprintf`, `__quadmath_printf_fp` and `__quadmath_mpn_mul` have defined
code-section addresses. This is stronger evidence than merely finding a
reference string. The wheel's separate libquadmath entry identifies it as
LGPL-2.1-or-later and statically linked into OpenBLAS; the GCC Runtime Library
Exception in the preceding libgfortran entry does not extend automatically to
libquadmath. The LGPL text and libquadmath's source notices are preserved.
[NumPy wheel licensing source](https://github.com/numpy/numpy/blob/v1.26.4/LICENSES_bundled.txt),
[GCC 10.3 libquadmath license](https://github.com/gcc-mirror/gcc/blob/releases/gcc-10.3.0/libquadmath/COPYING.LIB).

The DLL also contains defined MinGW-w64 and winpthreads runtime code symbols.
The full upstream MinGW-w64 runtime notice, overall ZPL notice, authors,
winpthreads MIT/BSD notice and GCC runtime terms are preserved byte-for-byte in
`third_party/numerical-supplemental/`, with provenance and scope in its README.
These supplement the wheel's own OpenBLAS/LAPACK/GFortran/libquadmath notices.

## Exact source and build inputs preserved

All archives below are present under `.artifacts/license-sources/numerical/`;
`NUMERICAL-SOURCE-MANIFEST.json` supplies their full SHA-256 hashes and URLs.
They must be copied into the release's corresponding-source companion before
publication. Research JSON/HTML caches and unpacked build directories are not
substitutes for these archives.

| Component | Preserved input | Provenance |
| --- | --- | --- |
| OpenBLAS | `OpenBLAS-c2f4bdbbb43a1d20a7342f40122e18e573ce436a.tar.gz` | Exact source revision named by NumPy's `v0.3.23-293-gc2f4bdbb` dependency |
| GCC/libgfortran/libquadmath | `gcc-10.3.0.tar.xz` | Complete GCC 10.3.0 release source; hash matches Rtools' pinned PKGBUILD |
| Rtools UCRT patches/build recipes | `rtools-ucrt-c5344cc8c7e310ee4eee513b2381af2e75d65cb9.zip` | Archived source state immediately preceding the compiler bundle's release |
| MinGW-w64 CRT/headers | `mingw-w64-acc9b9d9eb63a13d8122cbac4882eb5f4ee2f679.tar.gz` | Exact commit named by that Rtools source recipe; its patches are in the preceding archive |
| OpenBLAS Windows builder | `openblas-libs-ab19bb248c8f62064d7b83d6f7427ee95eb02fab.zip` | Historical builder snapshot immediately preceding the original DLL's PE timestamp |
| NumPy | `numpy-1.26.4.tar.gz` | Original PyPI source distribution; hash matches PyPI metadata |

The historical builder snapshot has a BSD-2-Clause top-level license and also
contains `objconv/source.zip`, the complete GPL-licensed object-converter tool
source with its own notice. That tool is not used by the Windows reconstruction
and is not added to the application binary. Its source and notice remain intact
inside the preserved snapshot; the companion also includes the full GPLv3 text
at `project/third_party/numerical-supplemental/GCC-COPYING3.txt`.

NumPy pins the long OpenBLAS revision and `win_amd64-gcc_10_3_0` artifact suffix
in [its release helper](https://github.com/numpy/numpy/blob/v1.26.4/tools/openblas_support.py).
The [historical Windows workflow](https://github.com/MacPython/openblas-libs/blob/ab19bb248c8f62064d7b83d6f7427ee95eb02fab/.github/workflows/windows.yml)
pins Rtools `4.0.0.20220206`, `MSYSTEM=UCRT64`, `INTERFACE64=1` and linker flags
`-lucrt -static -static-libgcc` for x64. Its
[build script](https://github.com/MacPython/openblas-libs/blob/ab19bb248c8f62064d7b83d6f7427ee95eb02fab/tools/build_openblas.sh)
supplies the BLAS options listed below. The snapshot is consistent with the
binary's timestamp and source identifier; expired historical CI records do
not independently prove the exact producer run.

The [Rtools documentation](https://cran.r-project.org/bin/windows/Rtools/rtools40.html)
identifies its `ucrt64` compiler as GCC 10.3.0. The downloaded official portable
`rtools40-x86_64.7z` from the **2022-02-06** release contains GCC/GFortran
**10.3.0-9804**, binutils **2.36.1-9800**, and MinGW-w64
**9.0.0.6214.acc9b9d9e-1**, confirmed by the archive's local pacman database.
Compiler execution and its complete `gcc -v` configuration were recorded in
`toolchain-probe.log`. The GCC tarball's SHA-256
`64f404c1a650f27fc33da242e1f2df54952e3963a49e06e73f6940f3223ac344`
matches [the preserved GCC build recipe](https://github.com/r-windows/rtools-ucrt/blob/c5344cc8c7e310ee4eee513b2381af2e75d65cb9/mingw-w64-gcc/PKGBUILD).

The compiler bundle is a **local build prerequisite**, not part of the proposed
source-only release companion. Shipping that bundle would require separately
accounting for all of its tools and dependencies. It can be extracted and used
without a system installer or registry changes.
[Official portable Rtools release](https://github.com/r-windows/rtools-installer/releases/tag/2022-02-06).

## Original build configuration

The reconstruction uses the historical recipe's options:

```text
BINARY=64 DYNAMIC_ARCH=1 USE_THREAD=1 USE_OPENMP=0
NUM_THREADS=24 NO_WARMUP=1 NO_AFFINITY=1 CONSISTENT_FPCSR=1
BUILD_LAPACK_DEPRECATED=1 TARGET=PRESCOTT BUFFERSIZE=20
MAX_STACK_ALLOC=2048 INTERFACE64=1 SYMBOLSUFFIX=64_
LDFLAGS=-lucrt -static -static-libgcc
COMMON_OPT=-O2 -march=x86-64 -mtune=generic -fno-asynchronous-unwind-tables
FCOMMON_OPT=<COMMON_OPT> -frecursive -ffpe-summary=invalid,zero -fdefault-integer-8
LIBNAMESUFFIX=v0.3.23-293-gc2f4bdbb-gcc_10_3_0
```

The local script `rebuild-openblas.sh` uses those flags against the preserved
OpenBLAS source archive. It replaces the recipe's network/Git cleanup steps
with explicit source extraction and a fixed library suffix, so it does not
require a live remote or alter the repository's development checkout. It does
not replace the installed or packaged runtime DLL. See the
[upstream DLL link rule](https://github.com/OpenMathLib/OpenBLAS/blob/c2f4bdbbb43a1d20a7342f40122e18e573ce436a/exports/Makefile).

The original helper's Anaconda `openblas-libs` binary/static-archive endpoint
now returns an HTML page or API 404. That download is **not** counted as a
preserved binary archive; the HTML cache is named accordingly. Complete source,
the matching compiler bundle, build scripts, and locally generated relink
inputs provide a route independent of the retired endpoint.

## Build/relink verification

**Completed.** The full historical-configuration OpenBLAS source build finished
with exit code 0, including all 14 CPU families, BLAS, CBLAS, LAPACK and LAPACKE.
The build summary and exact GCC configuration are preserved under
`numerical-relink/evidence/`. Build completion alone is not a claim that every
upstream test executable was run; the executed replacement checks are below.

The original-source and marked-modification standalone libquadmath builds
completed both in the first build tree and in a freshly prepared second
workspace. A program linked with the modified archive called the added query
and computed/formatted `sqrtq(2)` as `1.41421356237309504880168872421`.
The dated patch adds the harmless query to `quadmath-printf.c`; the numerical
functions remain unchanged. Full source, patch and reconstruction instructions
are provided in `numerical-relink/README.md`.

Three separate replacement proofs passed under the unchanged NumPy 1.26.4
wheel, copied into disposable directories and loaded in fresh Python processes:

| DLL variant | Named exports | Numerical comparisons | Maximum absolute difference |
| --- | --- | --- | --- |
| Ordinary full OpenBLAS rebuild | All 9,360 original names | 12 passed | 0.0 |
| Full-tree relink with source-modified libquadmath | All 9,360 original names plus query | 12 passed | 0.0 |
| Object-only relink in the fresh workspace | All 9,360 original names plus query | 12 passed | 0.0 |

The comparisons exercise float32, float64, complex64 and complex128 matrix
multiplication, solve and SVD values; solve/SVD reconstruction residual checks
also pass. Both modified DLLs return
`ProcGen libquadmath source modification 2026-10-26`. Their link maps identify
the independently rebuilt `build/quadmath/.libs/libquadmath.a`, including the
printf object containing the change. All variants report the same ILP64,
dynamic-architecture and 24-thread configuration as the original.

The verifier explicitly parses all named PE exports: this library exceeds
pefile's default 8,192-name safety limit. It asserts the parsed count equals
`NumberOfNames`, avoiding a truncated export comparison.

The installed original DLL's SHA-256 remained
`57b87772bf676b5c2d718c79dddc9f039d79ec3319fee1398cc305adff7b69e5`
before and after every proof. No installed or packaged DLL was replaced.
Complete loaded paths, DLL hashes, export results and numerical differences are
in `numerical-relink/evidence/ordinary-rebuild-verification.json`,
`relink-verification.json` and `object-relink-verification.json`. The latter two
filenames are in the same evidence directory. These are technical library
reconstruction checks; application desktop and separate-PC acceptance remain
separate tests.

## Supplied application objects for prompt relinking

`NUMERICAL-RELINK-INPUTS.json` describes the actual, hash-verified generated
materials staged under `.artifacts/license-sources/numerical/relink-inputs/` for
the companion's `generated/numerical/` directory. The application object archive
is **45,270,754 bytes**, SHA-256
`08cd5d3b569dd5904d60ce991207a4be4679420728fcd92043618eea40faa992`.
It contains the OpenBLAS/LAPACK application objects before GNU runtime archives
are resolved during the DLL link. It is accompanied by the generated export
definition, `dllinit.obj`, configuration reference files, checksums and notices.
No compiler/toolchain binaries are included in these generated inputs.

The tested `relink-objects.sh` shortcut uses only those application objects and
the newly built libquadmath, with the separately obtained matching compiler's
runtime libraries. It was executed in the fresh workspace, where OpenBLAS had
not been compiled. Recipients can modify and rebuild libquadmath and relink
promptly without repeating the full DYNAMIC_ARCH build. The complete original
sources remain included for the full reconstruction route.

## Release requirements not discharged by this note

The LGPL-2.1 route requires the applicable notices/source delivery and materials
enabling modification/relinking; a copyright text or source URL alone is not a
complete solution. Preserve all original notices, the source/patch archives,
build and relink scripts, required generated configuration/definition files,
and the verification record in the same corresponding-source companion as the
public binary distribution. The chosen source-delivery method and final
combined-work terms still require review against the actual shipped files.
[LGPL-2.1 sections 4–6](https://github.com/gcc-mirror/gcc/blob/releases/gcc-10.3.0/COPYING.LIB).
