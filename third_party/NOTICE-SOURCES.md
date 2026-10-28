# Supplemental notice provenance

All package-supplied notices are copied from the pinned installed distributions
by `scripts/collect_licenses.py`; archive hashes are in the requirements lock
files. Supplemental files below fill omissions in those distributions. No
upstream game or font data was edited. Retrieved 2026-10-25.

| Local file(s) | Exact upstream source |
| --- | --- |
| `procgen/ASSET_LICENSES.md` | https://github.com/openai/procgen/blob/5e1dbf341d291eff40d1f9e0c0a0d5003643aebf/ASSET_LICENSES.md |
| `gym3/LICENSE`, `gym3/LICENSES.md` | https://github.com/openai/gym3/tree/2ed9d344ede8bbd96b6280e9fbbbf55861ea33a9 (v0.3.3) |
| `glfw/GLFW-3.3.2-LICENSE.md` | https://github.com/glfw/glfw/blob/3.3.2/LICENSE.md |
| `qt/LICENSE.LGPL3`, `qt/LICENSE.GPL3` | https://github.com/qt/qtbase/tree/v5.13.2 |
| `qt/third-party/libpng-LICENSE` | https://github.com/qt/qtbase/blob/v5.13.2/src/3rdparty/libpng/LICENSE |
| `qt/third-party/pcre2-LICENCE` | https://github.com/qt/qtbase/blob/v5.13.2/src/3rdparty/pcre2/LICENCE (includes SLJIT) |
| `qt/third-party/zlib-LICENSE` | https://github.com/qt/qtbase/blob/v5.13.2/src/3rdparty/zlib/LICENSE |
| `python/expat-COPYING` | https://github.com/python/cpython/blob/v3.10.1/Modules/expat/COPYING |
| `python/zlib-LICENSE` | https://github.com/python/cpython-source-deps/blob/zlib-1.2.11/README (complete upstream README including license) |
| `python/xz-COPYING` | https://github.com/python/cpython-source-deps/blob/xz-5.2.2/COPYING |
| `numpy/LGPL-2.1.txt` | https://github.com/gcc-mirror/gcc/blob/releases/gcc-10.3.0/COPYING.LIB |
| `python/sqlite-public-domain.txt` | Opening comment of https://github.com/python/cpython-source-deps/blob/sqlite-3.35.5.0/sqlite3.h |
| `tcl/license.terms` | https://github.com/tcltk/tcl/blob/core-8-6-12/license.terms |
| `tk/license.terms` | https://github.com/tcltk/tk/blob/core-8-6-12/license.terms |

Additional completion records, 2026-10-26 through 2026-10-28:

- Qt's complete qtbase attribution/notice superset is under `qt/source-notices/`,
  with its generated index in `qt/attribution-index.json` and readable
  `qt/ATTRIBUTIONS.md`. These are collected from the pinned official source
  archive in `source-archives.json`, not inferred from pip metadata.
- `numerical-supplemental/NOTICE-PROVENANCE.json` records the exact MinGW-w64,
  pthread, GCC and runtime-exception notice sources.
- `microsoft/README.md` and `docs/licensing/MICROSOFT-RUNTIME.md` record the
  controlled official runtime-package source, installed Visual Studio
  entitlement, signed DLL hashes and original terms.
- `assets/provenance.json` records the complete CC0/CC BY/OGA-BY legal texts.
- `cffi/native-notice-provenance.json` records libffi copyright/license headers
  omitted from the CFFI wheel's notice set.
- `python/OpenSSL-1.1.1l-LICENSE` is from
  https://github.com/openssl/openssl/blob/OpenSSL_1_1_1l/LICENSE (SHA-256
  `c32913b33252e71190af2066f08115c69bc9fddadf3bf29296e20c835389841c`).
- The FreeType acknowledgement covers Qt's rasterizer (2000-2016) and Pillow's
  FreeType 2.14.3 (2026); the latter version and year are in
  https://github.com/freetype/freetype/blob/VER-2-14-3/README.

Source delivery uses the matching actual corresponding-source companion ZIP.
See `SOURCE-COMPANION.md` in the bundled licenses and the project's current
redistribution record; a notice collection alone is not source delivery.
