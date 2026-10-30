# Controlled Microsoft runtime distribution - 2026-10-28

## Current selection

Use the official stable **VC14 14.51.36247.0 x64** package as a controlled
build-only extraction input under the installed **Visual Studio Community
2022** license and its REDIST list. Keep the existing unchanged GLFW 3.3.2
VS2019 /MD build. Omit obsolete VC11, app-local UCRT and API-set files;
Windows 10/11 supplies the latter. No installer, MSI, installed Python package,
registry setting, or system file is modified.

The previous VS2019 14.29 runtime's exports covered the app's imported symbols,
but that did not satisfy Microsoft's version requirement: Pillow, ModernGL,
and glcontext binaries have linker version 14.51, and CFFI has 14.41. The
selected runtime must also be at least as new as the newest component toolset.
[Microsoft binary compatibility documentation](https://learn.microsoft.com/en-us/cpp/porting/binary-compat-2015-2017)
establishes this requirement. Matching exported names alone is insufficient.

## Permission, original terms, and downstream agreement

The installed Community 2022 license's section 1(b)(i) permits development of
applications released under OSI-approved licenses. This independent MIT
project meets that session-established scope without an organization-size
question. Section **4** grants object-code distribution from its REDIST list
and permits downstream application distributors. Original terms are retained
in `third_party/microsoft/VS-Community-2022-EULA.docx` (EULA ID
`VS_Comm_2022_ENU.1033`) and the required `.txt` reading copy. The
[official document](https://visualstudio.microsoft.com/wp-content/uploads/2021/11/Visual-Studio-2022-Community-License-EN.docx)
has SHA-256 `41a207b10c8ab91d0d2f10a854715f73dca54509581692d2fe179aa3ffcb8540`.
Word's generated numbering is not reproduced in the paragraph-text extraction;
the original DOCX controls.

The [2022 REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution)
names Community 2022 and expressly permits licensed users to distribute
packages or individual binaries obtained from the latest-supported download
page. The [latest-supported page](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)
shares the supported v14 family across VS2017-2026 and recommends it for
VS2019/2022 applications. The selected package is from its stable x64 link,
not a Preview/Pre-release/Beta runtime prohibited by the Community terms.
The installed VS2022 Community redist folder contains servicing metadata only;
no absent local DLLs or unrelated PATH copies are used as the source.

Section 4(b) requires protective downstream agreement. Its exact condition is:

> require distributors and external end users to agree to terms that protect the Distributable Code at least as much as this agreement.

The license specifies no particular checkbox, clickwrap, installer, or
first-launch UI. The implementation supplies component-scoped
`third_party/microsoft/DOWNSTREAM-TERMS.md`, conditions use/redistribution of
Microsoft code on agreement, and presents the condition in README and notices.
A hidden EULA alone would not implement that condition. Wording is not proof
of an individual recipient's assent in every jurisdiction; no such proof is
claimed. The original terms and non-waivable local rights control.

Those conditions apply only to Microsoft code. They do not relicense MIT,
PSF, zlib, LGPL, or other components, nor restrict their source access,
modification, relinking, or debugging rights under their own licenses/law.
The retained original [CPython notice](https://github.com/python/cpython/blob/v3.10.1/PC/crtlicense.txt)
addresses Microsoft code in the Windows interpreter; it is not blanket
permission for arbitrary DLLs. The standalone runtime installation/use EULA
is likewise not the redistribution grant: the Community license plus its
explicit REDIST download provision supplies this project's route. The 2019
Community original terms remain for the unchanged GLFW toolchain.

## Pinned download and extraction evidence

The stable alias `https://aka.ms/vc14/vc_redist.x64.exe` resolved on 2026-10-28
to this immutable official source, which the helper downloads directly:

```text
https://download.visualstudio.microsoft.com/download/pr/ebdab8e5-1d7b-4d9f-a11b-cbb1720c3b12/843068991DAAA1F73AD9F6239BCE4D0F6A07A51F18C37EA2A867E9BECA71295C/VC_redist.x64.exe
```

Package SHA-256:
`843068991daaa1f73ad9f6239bce4d0f6a07a51f18c37ea2a867e9beca71295c`.
Version: **14.51.36247.0**. Authenticode: **Valid**, Microsoft Corporation.
The helper locks both package version and hash and validates its signature
before extraction. It reads the signed package's Burn v2 container header,
validates flat CAB member paths, writes its two cabinets as data, and calls
Windows' built-in `expand.exe`. It does **not** execute the EXE or any MSI,
including for an installer layout operation. The Burn payload manifest maps
the x64 minimum CRT cabinet (`packages/vcRuntimeMinimum_amd64/cab1.cab`);
its declared length/hash is checked before expansion. Cabinet structure facts
are documented in the [first-party WiX Burn source](https://github.com/wixtoolset/wix3/blob/develop/src/burn/engine/section.cpp).
The helper implements the small format reader, without copying WiX code.

Each selected DLL must have x64 PE architecture, the exact locked DLL hash,
the same **14.51.36247.0** file version, and a valid Microsoft signature.
The observed signer is Microsoft Windows Software Compatibility Publisher,
organization Microsoft Corporation. Exact hashes, extraction mapping,
package/DLL signatures and source provenance are retained in
`third_party/microsoft/RUNTIME-PROVENANCE.json` and the generated manifest.

The selected dependency closure is `msvcp140.dll`, `vcruntime140.dll`, and
`vcruntime140_1.dll`. Their own normal and delay imports are inspected
recursively. Any new MSVC14 dependency without a controlled hash fails
preparation. Windows API DLLs/UCRT contracts remain system-provided.
The other CRT/OpenMP/MFC/ARM64 components in the package are not copied.

## Unchanged GLFW build

The original wheel's GLFW3 DLL imports `MSVCR110.dll`. Rebuild the exact,
unmodified GLFW **3.3.2** tag to remove that independent VC11 requirement:

- Commit: `76dfe13e4ee7c739156260053bc40c938679c754`.
- Archive: https://codeload.github.com/glfw/glfw/zip/refs/tags/3.3.2
- SHA-256: `33c6bfc422ca7002befbb39a7a60dc101d32c930ee58be532ffbcd52e9635812`.
- VS16 2019 generator, v142, x64, SDK10.0.19041.0, Release, shared, /MD
  (`USE_MSVC_RUNTIME_LIBRARY_DLL=ON`). Examples/tests/docs/install disabled.
- Original Win32/WGL/EGL/OSMesa paths enabled; upstream Vulkan loader default.
- Version API: `3.3.2 Win32 WGL EGL OSMesa VisualC DLL`; no VC11 imports.

Only this viewer dependency is rebuilt; ProcGen engine/assets/gameplay are
unchanged. The DLL is locally built and not Microsoft-signed. Its exact hash,
source archive, commands, compiler configuration and logs are in the manifest.
Preparation reuses an existing hash-verified build and its provenance unless
`--rebuild-glfw` is specified; the runtime update preserves that existing DLL.
The Python GLFW binding's package fallback explicitly preloads VC11, so the
packaging runtime hook sets its existing `PYGLFW_LIBRARY` override to the exact
bundled rebuilt DLL before import. No installed wheel is patched.

## Reproduction and packaging contract

Prerequisites: Windows x64, project Python environment/pefile, and Visual Studio
2022 or 2019 with CMake/v142 tools plus SDK10.0.19041.0 for a fresh GLFW build.
The project's Community-developed open-source redistribution route remains as
documented above. It does not require a Community IDE on every build worker:
GitHub-hosted `windows-2022` uses its preinstalled VS2022 Enterprise build tools.
The helper records detected build installations separately from the project's
redistribution terms. CRT downloads, hashes, signatures and dependency checks
are identical on both platforms; ambient PATH runtimes are never a fallback.

```powershell
.\.venv\Scripts\python.exe scripts/prepare_windows_runtime.py --download --check-bundle dist/ProcGenPlayground
```

`--download` fetches pinned Microsoft/GLFW inputs only when absent, at build
time. Omit it to prepare offline from cached inputs. No application download
occurs. The Microsoft EXE remains under ignored `.artifacts/license-sources/`
and is excluded from both release archives; the source companion carries the
recipe, original licenses and provenance instead. GLFW source is included.

The generated `.artifacts/licensed-runtime/manifest.json` retains `vc14.files`
project-relative staged paths/hashes/versions/signatures and `glfw` source,
build and output records. Packaging replaces every same-named analyzed CRT
with those files, substitutes only GLFW's native DLL, and omits
`msvcr110.dll`, `msvcr100.dll`, `ucrtbase.dll`, and `api-ms-win-*.dll`.
Retain all component terms/notices and include provenance/recipes.

`verify_msvc_exports` checks normal/delay imports and required symbols,
rejects uncontrolled MSVC14 DLL names, verifies coherent staged versions,
and checks the staged runtime's own dependency closure. For each native
file importing this runtime it also compares its PE Major/MinorLinkerVersion
against the selected runtime's major/minor version. Thus 14.52-linked code
is rejected with a 14.51 runtime even if every symbol happens to exist.
The full per-file check is recorded in the manifest. PE linker fields are an
observable toolset floor, not complete compiler provenance or build-patch
proof; dependency updates still require reviewing their build provenance.

[Microsoft documents UCRT](https://learn.microsoft.com/en-us/cpp/windows/universal-crt-deployment)
as an OS component on Windows10/11. [API-set documentation](https://learn.microsoft.com/en-us/windows/win32/apiindex/windows-apisets)
explains that contract names resolve through the loader; their import names
do not require copied files from PATH. This build supports Windows10/11 only.
Native/frozen fidelity, isolated DLL loading and final desktop/separate-PC
checks remain distinct evidence; this preparation does not claim another
machine was tested. Other components' corresponding-source/relink duties
are addressed separately.
