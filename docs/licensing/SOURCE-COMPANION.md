# Corresponding source companion

The portable program is distributed with a companion archive named
`ProcGenPlayground-corresponding-sources.zip`. Publish both ZIPs and both
SHA-256 files together, on the same release/download page, with equally
accessible source downloads and no additional source-access charge. Retain
the exact source companion for every binary release. A link to a moving
upstream branch or a promise to assemble sources later is not the delivery
method selected for this project.

The companion contains the complete pinned Qt/qtbase, ProcGen, gym3, GLFW, CFFI,
OpenBLAS and GCC/runtime sources, the historical numerical build recipes and
patches, this project's source and licenses, and rebuild/relink instructions.
`third_party/source-archives.json` locks archive URLs, revisions, sizes and
SHA-256. These source archives are actual included files, not just download links.
The combined source archive also records the exact portable ZIP checksum.

## Qt / ProcGen rebuilding and replacement

The supplied Windows helper `project/scripts/rebuild_procgen_native.py` builds
Qt 5.13.2 statically with ProcGen's original options and namespace, then builds
the unmodified ProcGen 0.10.7 engine using its CMake configuration and the
supplied gym3 C API header. It supports a separately modified Qt source tree.
The release engine is still the original wheel binary, not the verification
build. No game rules or assets are modified.

Prerequisites: Windows x64, Python 3.10, Visual Studio 2019 with x64 C++ tools
and Windows SDK, its CMake component, and Perl (for example Git for Windows'
bundled Perl). These are general-purpose build tools, separately obtained under
their own terms. The source helper never installs tools or compiles at gameplay
runtime. Use a short build path without spaces; Qt 5.13 does not support spaces
in its build directory. Compiling Qt requires substantial disk space and time.

After extracting this source companion, from its top-level directory:

```powershell
python project/scripts/rebuild_procgen_native.py --archives archives --work D:/ProcGenRelink
```

Default Visual Studio location is the installed VS2019 BuildTools folder. Use
`--visual-studio` to select another VS2019 installation containing CMake/C++.
Logs and `rebuild-report.json` are written beneath the work directory.

On long Windows workspace paths the helper canonicalizes generated one-line Qt
forwarding includes to the same target files. This avoids MSVC's legacy path
limit without changing Qt implementation code or API. It also normalizes
Windows environment variable name casing for MSBuild. Neither step modifies
the original source archives.

To modify Qt, extract `archives/qtbase-everywhere-src-5.13.2.tar.xz`, change the
desired library source, then use a **new** work directory with
`--qt-source D:/YourModifiedQtSource`. Do not reuse a build configured against
a different source tree. To reuse the already built Qt in the same work
directory while only rebuilding the engine, add `--qt-built`.

With the app closed, make a disposable copy of the entire extracted portable
folder and replace only:

```text
ProcGenPlayground/_internal/procgen/data/prebuilt/env.dll
```

with `engine-build/RelWithDebInfo/env.dll` from your work directory. The normal
launcher loads this path; no signature lock, hash enforcement, encryption or
runtime download prevents replacement. Keep the assets and other dependencies
together. If your modification changes the C API, update the corresponding
caller as needed; retaining the interface is the simplest replacement route.

Verification on 2026-10-26 used MSVC 14.29.30133 and Windows SDK 10.0.19041.0.
`qt-version-marker.patch` demonstrates a harmless Qt `qVersion()` change.
The modified Qt Core was rebuilt, linked into an otherwise unmodified engine,
and loaded from a disposable packaged-app copy. Nine native cases still
matched upstream. The JSON evidence is under `project/docs/verification/`.
The modified verification DLL is not the engine distributed with the game.

## Numerical and viewer libraries

The numerical source/build/replacement procedure is in
`project/docs/licensing/NUMERICAL-SOURCES.md`. It covers the LGPL libquadmath
component statically contained in NumPy's OpenBLAS DLL, separately from
libgfortran's GCC Runtime Library Exception.

This prepared release companion also supplies verified OpenBLAS application
objects under `generated/numerical/`, for a faster relink after modifying
libquadmath. These inputs and hashes are listed in the companion's
`manifest.json` and `project/docs/licensing/NUMERICAL-RELINK-INPUTS.json`.
For a fresh build where these generated inputs have not been staged, the
packager retains the complete source reconstruction route and records an empty
`numerical_relink_inputs` list; the optional shortcut is then unavailable.
It rejects a partially staged or altered object set.

The same-version GLFW rebuild, controlled Microsoft CRT provenance, and
component-specific Microsoft terms are in
`project/docs/licensing/MICROSOFT-RUNTIME.md` and
`project/third_party/microsoft/`. Microsoft runtime binaries are distributed
with the application, not misrepresented as open-source library source here.

All components retain their respective licenses. Nothing in the application's
MIT license or Microsoft-only component terms limits Qt/libquadmath source,
modification, replacement, relinking or debugging rights under their licenses.
