# Third-party provenance and redistribution status

ProcGen Playground is an independent wrapper, not an official OpenAI product.
Wrapper source is under the root MIT license. Bundled dependencies, fonts,
artwork and Microsoft runtime files retain their separate licenses. The ZIP
is not wholly MIT.

This application uses **Qt 5.13.2**, statically linked into ProcGen's `env.dll`,
under the LGPLv3 open-source option. Qt is copyright The Qt Company and other
contributors. LGPLv3 and GPLv3 texts are in `third_party/qt/`. Corresponding
source and relinking materials are provided in the matching actual
`ProcGenPlayground-corresponding-sources.zip`; see `SOURCE-COMPANION.md` and
`REDISTRIBUTION.md`. Preserve access to that source archive with the binary.

## ProcGen

- Package: OpenAI ProcGen 0.10.7, CPython 3.10 `win_amd64` wheel from PyPI.
- Engine and Python package are unmodified; the wrapper calls
  `procgen.interactive.make_interactive` directly.
- Code: MIT; included at `third_party/procgen/LICENSE`.
- Assets: multiple licenses; the upstream asset notices must be included in
  `third_party/procgen/ASSET_LICENSES.md`.
- Source: https://github.com/openai/procgen
- Source tag: `0.10.7`, commit `5e1dbf341d291eff40d1f9e0c0a0d5003643aebf`.
- Assets are redistributed unchanged; their individual authors and license
  links appear in the bundled original `ASSET_LICENSES.md`.
- Asset licenses are CC0, CC BY 3.0/4.0, and OGA-BY 3.0, with terms at:
  https://creativecommons.org/publicdomain/zero/1.0/,
  https://creativecommons.org/licenses/by/3.0/,
  https://creativecommons.org/licenses/by/4.0/,
  https://opengameart.org/content/oga-by-30-faq.

## Bundled dependencies

The build collects installed distribution license files and CPython's license
into `third_party/`. The pinned dependency inventory is in
`requirements-windows.txt`. gym3, GLFW, ModernGL, NumPy, Pillow, CFFI, and the
other libraries retain their respective licenses. PyInstaller's bootloader
exception applies to the frozen application's distribution.

The bundled notice inventory includes build-tool notices as well as runtime
notices; inclusion there does not mean every listed package is shipped as code.
The installed ImageIO-FFmpeg dependency is excluded from the portable build;
video recording is not exposed and no FFmpeg executable should be distributed.
Tcl/Tk notices are from the upstream `core-8-6-12` tags:
https://github.com/tcltk/tcl/blob/core-8-6-12/license.terms and
https://github.com/tcltk/tk/blob/core-8-6-12/license.terms.

Additional native/font notices:

- gym3 0.3.3 code is MIT (OpenAI 2020); `third_party/gym3/LICENSE`.
- Its unchanged Terminus Font is OFL-1.1, copyright Dimitar Toshkov Zhekov
  2019, reserved name "Terminus Font"; complete notice: `third_party/gym3/LICENSES.md`.
- Python glfw 1.12.0 is MIT; its native GLFW 3.3.2 library is zlib licensed,
  with the separate notice `third_party/glfw/GLFW-3.3.2-LICENSE.md`.
- NumPy's combined notice includes OpenBLAS, LAPACK and the GCC runtime with
  its exception. Separately, libquadmath statically included in OpenBLAS is
  LGPL-2.1-or-later (`third_party/numpy/LGPL-2.1.txt`); its source/relinking
  sources, build/relink helpers and replacement evidence are in the companion.
  Pillow's combined notice includes its codec
  and font-library terms. For FreeType we use the permissive FreeType License
  alternative: portions of this software are copyright (c) 2000-2026 The FreeType Project
  (www.freetype.org). All rights reserved.
- This product includes software developed by the OpenSSL Project for use in
  the OpenSSL Toolkit (http://www.openssl.org/), and cryptographic software
  written by Eric Young (eay@cryptsoft.com). CPython's Windows LICENSE includes
  the OpenSSL/SSLeay, bzip2 and libffi notices; supplementary Python-native
  notices are in `third_party/python/`.
- Microsoft VC/UCRT binaries have Microsoft redistribution terms, not MIT.

Supplemental Qt notices preserve the complete qtbase attribution superset,
including full license texts. Numerical supplements cover MinGW-w64, pthread,
OpenBLAS x64/LAPACKE and GCC notices absent from the wheel's aggregate notice.
The same-version GLFW library was rebuilt from unchanged 3.3.2 source using
VS2019/VC14, removing the old VC11 dependency. Three signed, hash-locked VC14
DLLs come from a hash-locked official Microsoft VC14 redistribution package,
under the installed Visual Studio Community open-source development route.
Microsoft-only terms are in `third_party/microsoft/DOWNSTREAM-TERMS.md` and are
prominently communicated in the portable README and THIRD-PARTY-NOTICES.txt.

No public release has been published. Final desktop/separate-PC acceptance and
publication of the binary/source pair remain release steps. Current technical
redistribution preparation: `REDISTRIBUTION.md`. Supplemental notice provenance:
`third_party/NOTICE-SOURCES.md`.
