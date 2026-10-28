# Dependency license audit — 2026-10-25

> Historical initial audit. The source/notices/runtime preparation that followed
> is recorded in `docs/licensing/REDISTRIBUTION.md` (2026-10-28), with actual
> corresponding-source delivery described in `docs/licensing/SOURCE-COMPANION.md`.
> The unchecked items below describe the initial findings, not the current status.

## Recommendation

Retain **MIT for our launcher and build scripts**. It allows reuse,
modification, redistribution and commercial use with the copyright/license
notice retained. GPLv3 is an alternative if the owner wants distributed
derivatives to remain open source; PyInstaller does not require that choice.
The root license does not replace bundled dependencies' licenses.

**Public binary redistribution is not yet cleared:** Qt source/relinking
materials, NumPy/libquadmath obligations and Microsoft redistribution provenance
remain open. This audit
examined pinned installed distributions, actual license files, frozen native
binaries, tagged upstream build scripts, and official licensing documentation.
It is a technical compliance audit, not a legal opinion on contractual rights.

## Package inventory

Notices live in `third_party/`. The generated `inventory.json` preserves raw
metadata and labels build tools/excluded packages. UNKNOWN metadata is not a
license: ProcGen and gym3 have MIT licenses in their tagged sources.

| Component | Version | License / treatment |
| --- | --- | --- |
| Our launcher | 0.2.0.dev0 | MIT |
| ProcGen code | 0.10.7 | MIT, OpenAI notice preserved |
| ProcGen artwork | upstream 0.10.7 | CC0, CC BY 3.0/4.0, OGA-BY 3.0; original author/source notices retained; unchanged |
| gym3 | 0.3.3 | MIT; missing wheel notice supplied from exact source tag |
| Terminus font | bundled font.bin | OFL-1.1; full copyright, reserved name and license added |
| gym | 0.26.2 | MIT |
| gym-notices | 0.1.0 | MIT, confirmed in LICENSE.txt |
| filelock | 3.32.7 | MIT |
| CFFI | 1.17.1 | MIT; native libffi notice included with Python |
| pycparser | 3.11 | BSD-3-Clause |
| glfw Python bindings | 1.12.0 | MIT |
| GLFW native DLL | 3.3.2 | zlib; separate native notice added |
| ModernGL / glcontext | 5.13.0 / 3.1.0 | MIT |
| NumPy | 1.26.4 | BSD-3-Clause plus numerical-library notices/exceptions |
| Pillow | 12.3.0 | MIT-CMU plus codec/font notices |
| ImageIO | 2.38.0 | BSD-2-Clause |
| imageio-ffmpeg wrapper | 0.3.0 | BSD; installed dependency, now excluded from portable artifact |
| FFmpeg executable | 4.1 | Old artifact contained GPL-enabled build; removed from new packaging |
| cloudpickle | 3.1.2 | BSD-3-Clause |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| CPython | 3.10.1 | PSF-2.0 and historical/embedded component licenses |
| Tcl/Tk | 8.6.12 | permissive Tcl/Tk notices |
| PyInstaller | 6.16.0 | GPL-2.0-or-later with bootloader/application exception; some Apache-2.0 files |
| PyInstaller hooks | 2026.9 | build hooks GPL-2.0-or-later; bundled runtime hooks Apache-2.0 |
| altgraph / pefile | 0.17.5 / 2023.2.7 | MIT, build dependencies |
| pywin32-ctypes | 0.2.3 | BSD-3-Clause, build dependency |
| setuptools | 80.9.0 | MIT, build dependency, excluded from frozen application |

Test/typecheck/bootstrap packages in the requirements are not all distributed
with the app. Local wheelhouse archives are ignored, not shipped; distributing
that development wheelhouse would require its own complete inventory.

## Qt static linking: remaining release work

The pinned ProcGen build specifies **Qt 5.13.2**, module **qtbase**, `-static`,
`-opensource`, namespace `ProcGenQt`, and links `Qt5::Gui`. Qt's Harfbuzz,
OpenSSL, OpenGL, JPEG, GIF and ICO features are disabled by that script.
`env.dll` contains `5.13.2` and `ProcGenQt` strings and has no Qt DLL imports.
This supports static linking; it does not prove that every build detail of the
PyPI wheel has been reconstructed.

Qt Core/Gui's LGPLv3 route requires the corresponding library source and
source/object code plus build materials allowing users to relink the combined
native library with modified Qt and run it. LGPLv3 section 4 permits application
terms of choice when its conditions are met, so our code can remain MIT.
Adding an LGPL text or a link alone does not satisfy the source/relinking duties.

Added LGPLv3/GPLv3 texts and explicit Qt attribution. Native strings also
identify libpng, PCRE and zlib; pinned Qt manifests name libpng 1.6.37,
PCRE2 10.33 and zlib 1.2.11. Their permissive notices are included. The final
embedded-component inventory needs actual configuration/build evidence;
these findings do not establish that there are no other embedded components.

- [ ] Preserve corresponding Qt 5.13.2/qtbase and engine sources with exact
  revisions, changes if any, and Windows toolchain/configuration details.
- [ ] Verify a documented `env.dll` rebuild/relink procedure, including the
  gym3 C API header, and replacement in the portable folder.
- [ ] Complete Qt's embedded-component inventory against the configuration and
  preserve applicable additional notices.
- [ ] Supply source/relinking materials alongside public binaries using a
  distribution method satisfying LGPL/GPL source-delivery requirements.

No commercial Qt license is assumed to exist.

## FFmpeg: unnecessary executable removed

ImageIO's packaging hook pulled in `ffmpeg-win64-v4.1.exe`. Its `-version`
output reports `--enable-gpl --enable-version3`, x264, x265 and many additional
codecs. ImageIO-FFmpeg's BSD wrapper license does not cover that executable.
Recording is not exposed; the spec now excludes `imageio_ffmpeg` and frozen
verification rejects any `*ffmpeg*.exe`. Upstream engine/game files remain
unchanged. Future recording support needs a separate FFmpeg/codec audit.

## Other native components

CPython's bundle includes OpenSSL DLLs, SQLite, Expat, bzip2, liblzma, libffi,
Tcl/Tk and standard extensions. Runtime checks report OpenSSL **1.1.1l**,
SQLite **3.35.5**, Expat **2.4.1**. The pinned CPython Windows external manifest
specifies bzip2 **1.0.6**, libffi **3.3.0**, xz **5.2.2**, zlib **1.2.11**.
Python's installed LICENSE includes OpenSSL/SSLeay, bzip2 and libffi terms.
Added Expat, zlib, SQLite's public-domain declaration and xz notices. Only
liblzma is used from xz; that version's license places the library in the
public domain, separately from its command-line tools' licenses. OpenSSL
acknowledgements are in ATTRIBUTION.md.

NumPy's wheel includes OpenBLAS **0.3.23**, with GCC **10.3.0** identified in
the DLL filename. The combined notice covers OpenBLAS (BSD-3-Clause), LAPACK
(BSD-3-Clause-Attribution), libgfortran (GPL-3.0 with GCC Runtime Library
Exception) and, separately, **libquadmath (LGPL-2.1-or-later)** statically
linked into the OpenBLAS DLL. The DLL contains quadmath function-name strings.
The libgfortran exception does not automatically exempt libquadmath. Added the
full LGPL-2.1 text; MIT on our code remains possible, but notices alone do not
complete this dependency's compliance requirements.

- [ ] Preserve the matching libquadmath source and OpenBLAS/GCC build details;
  establish and provide materials allowing the library's modification/relinking
  as required by the selected LGPL route, or verify a compliant alternative
  build. Include this in the final corresponding-source distribution review.

Pillow's combined notice includes brotli 1.2.0, FreeType 2.14.3, Harfbuzz 14.2.1,
LittleCMS 2.19.1, libavif 1.4.2, libjpeg-turbo 3.1.4.1, libpng 1.6.58,
libwebp 1.6.0, OpenJPEG 2.5.4, TIFF 4.7.1, xz 5.8.3 and zlib-ng 2.3.3,
including nested codec terms. These are wheel notice headings, not a claim
that every listed build helper is linked into the app. For FreeType use its
permissive **FTL** alternative and preserve the acknowledgement added to
ATTRIBUTION.md; the alternative GPL text is not the only licensing choice.

Microsoft VC140, UCRT/API-set DLLs and GLFW's `msvcr110.dll` are proprietary
redistributable code, not MIT. CPython's Windows notice includes distribution
conditions. Microsoft's VC110 redist list is subject to its applicable software
license, not an unconditional grant to every redistributor.

- [ ] Record provenance and applicable redistribution terms for each Microsoft
  runtime family; verify the publisher's entitlement and required downstream
  notices before publishing the ZIP.

## Audit corrections and validation

- Supplemental notices and provenance are recorded in `third_party/NOTICE-SOURCES.md`.
- The font matches gym3 v0.3.3 exactly: SHA-256
  `c2500c6605135c4b005b5234d80ff3d8f210d6222634a933bb0f4c59ecbeb083`.
- Notice collection now rejects executable/source files accidentally matched
  by filename, requires key notices, and labels build/excluded packages.
- Packaging excludes FFmpeg and artifact verification checks that exclusion.
- Full desktop walkthrough and separate-PC testing stay at final validation.

## Primary sources

- [MIT](https://opensource.org/license/mit)
- [Pinned ProcGen Qt build](https://github.com/openai/procgen/blob/0.10.7/procgen-build/procgen_build/build_qt.py)
  and [native link configuration](https://github.com/openai/procgen/blob/0.10.7/procgen/CMakeLists.txt)
- [gym3 license](https://github.com/openai/gym3/blob/v0.3.3/LICENSE)
  and [font notice](https://github.com/openai/gym3/blob/v0.3.3/LICENSES.md)
- [Qt obligations](https://www.qt.io/development/open-source-lgpl-obligations)
  and [LGPLv3 section 4](https://www.gnu.org/licenses/lgpl-3.0.html#section4)
- [FFmpeg licensing](https://ffmpeg.org/legal.html)
- [PyInstaller exception](https://pyinstaller.org/en/v6.16.0/license.html)
- [CPython Windows externals](https://github.com/python/cpython/blob/v3.10.1/PCbuild/get_externals.bat)
- [Microsoft redistribution terms](https://learn.microsoft.com/cpp/windows/redistributing-visual-cpp-files)
  and [VC110 list](https://learn.microsoft.com/en-us/visualstudio/releases/2012/2012-redistribution-vs)
- [GCC 10.3 libquadmath license](https://github.com/gcc-mirror/gcc/blob/releases/gcc-10.3.0/libquadmath/COPYING.LIB)
  and [LGPL-2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)
