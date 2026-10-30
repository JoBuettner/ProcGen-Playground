# Redistribution preparation

Updated 2026-10-28. This records the materials prepared for the portable Windows
build. It supersedes the open technical items in the historical 2026-10-25
license audit. The launcher remains MIT licensed; dependencies retain their own
terms. No public release has been published.

## Included materials

| Component | Materials and verification |
| --- | --- |
| ProcGen and gym3 | Original MIT notices, unchanged game assets and artist credits, all four asset license texts, Terminus font OFL notice |
| Qt 5.13.2 | LGPLv3/GPLv3 texts, 118 original qtbase notices/manifests covering 61 attribution entries, complete pinned source archive, original build configuration, rebuild/replacement helper and modified-Qt relink evidence |
| NumPy/OpenBLAS and libquadmath | Wheel notices, supplemental LAPACK/OpenBLAS/MinGW/pthread/GCC notices, complete pinned source/patch/recipe archives, source-build and relink helpers, ABI/numerical replacement verification records |
| GLFW 3.3.2 | Original zlib notice and source archive; same-version unmodified source rebuilt with VC14, avoiding its original VC11 runtime dependency |
| Microsoft runtime | Signed, hash-locked release CRT DLLs from an official Microsoft VC14 redistribution package under the installed Community license, original conditions and scoped downstream terms, prominent README/notice agreement condition |
| Python and other libraries | Collected package and CPython notices, original Tcl/Tk texts, CFFI native libffi notices, OpenSSL acknowledgements and exact license, Pillow codec/font notices |
| PyInstaller | Original license and bootloader exception; build-tool notice entries are distinguished from shipped runtime code |

Unused FFmpeg is excluded. UCRT and API-set DLLs come from supported Windows
10/11 rather than unrelated cached files. The controlled runtime helper and
artifact verifier check hashes, PE imports/exports and every shipped native
file's input provenance. The ProcGen engine and its 1,290 data files remain the
original wheel bytes; replacement-library experiments use disposable copies.

## Source delivery

`ProcGenPlayground-corresponding-sources.zip` contains actual pinned sources,
this project's source, complete notices, rebuild/relink scripts and evidence.
The manifest binds it to the exact portable ZIP checksum. The prepared companion
also includes verified OpenBLAS application objects and generated relink inputs
for the optional faster libquadmath replacement route. Compiler/toolchain
binaries are separately obtained prerequisites, not redistributed in that ZIP.

The source and binary ZIPs each have a SHA-256 sidecar. Publish them together,
with equally accessible downloads and no additional source-access charge, and
retain the matching source companion for each binary release. Preserve the
Microsoft component agreement condition prominently on the download page and
in the included notices. The source archive and local notices cannot by
themselves establish that a future download page satisfies these conditions.

## Evidence and remaining release steps

- Source and relink procedure: `SOURCE-COMPANION.md`.
- Qt build evidence: `qt-rebuild-manifest.json`, `qt-config-summary.txt`, and
  the modified-Qt records under `project/docs/verification/` in the companion.
- Numerical source identification, original and modified replacement results:
  `NUMERICAL-SOURCES.md`, `NUMERICAL-SOURCE-MANIFEST.json`, and
  `NUMERICAL-RELINK-INPUTS.json`.
- Controlled CRT and viewer preparation: `MICROSOFT-RUNTIME.md`.
- Final artifact verification: `.artifacts/license-bundle-verification.json`
  in the development workspace, produced by `scripts/verify_license_bundle.py`.

The final desktop walkthrough, separate PC without Python, actual
SmartScreen/antivirus observations, and publication remain release steps.
Those checks remain separately recorded. GitHub source checks have passed;
the updated packaging job uses GitHub-hosted Windows with the documented
compiler tools, and its first complete run remains to verify.

This is an engineering record of the actual sources, notices and replacement
procedures supplied, not a claim of legal clearance for every jurisdiction or
for arbitrary future changes to the distribution.
