# Microsoft runtime provenance and terms

The launcher remains MIT. Microsoft runtime code is separately licensed
Distributable Code. Read [DOWNSTREAM-TERMS.md](DOWNSTREAM-TERMS.md) before
using or redistributing those components; agreement is a condition of their use
and redistribution. Other components retain their own licenses and rights.

## Original terms retained

- `VS-Community-2022-EULA.docx`: original English Community 2022 license,
  EULA ID `VS_Comm_2022_ENU.1033`, retrieved 2026-10-28 from the
  [official Microsoft document](https://visualstudio.microsoft.com/wp-content/uploads/2021/11/Visual-Studio-2022-Community-License-EN.docx).
  SHA-256: `41a207b10c8ab91d0d2f10a854715f73dca54509581692d2fe179aa3ffcb8540`.
- `VS-Community-2022-EULA.txt`: paragraph-text extraction for reading. Word's
  generated list numbering is not reproduced; the unmodified DOCX controls.
- `VS-Community-2019-EULA.docx`: original English Community 2019 license,
  EULA ID `VS_Community_2019_ENU.1033`, retained for the GLFW build toolchain.
  Retrieved 2026-10-26 from the
  [official Microsoft document](https://visualstudio.microsoft.com/wp-content/uploads/2020/05/VS_Community_2019_ENU.1033.docx).
  SHA-256: `3dc17ec1490b436a97816aa4b06cc08eac9e37933a2813dbfa1886eaf23bde08`.
  Its `.txt` file is a reading copy.
- `CPython-3.10.1-crtlicense.txt`: unmodified
  [CPython Windows Microsoft-code notice](https://github.com/python/cpython/blob/v3.10.1/PC/crtlicense.txt),
  also present in the bundled Python license.

## Permission and controlled source

This independent MIT application uses the installed Community 2022 license's
OSI open-source development provision in section 1(b)(i). Section 4 permits
application distribution of code on its
[REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution).
That list expressly includes individual binaries obtained from Microsoft's
[latest-supported VC14 downloads](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170).
This license-plus-list route supplies permission; the standalone runtime
installation/use terms alone are not treated as a distribution grant.

The pinned stable x64 download is **14.51.36247.0**, retrieved 2026-10-28.
Its immutable Microsoft URL, package hash, valid Microsoft signature, CAB
extraction mapping, selected DLL hashes/signatures, and recursively inspected
imports are retained in [RUNTIME-PROVENANCE.json](RUNTIME-PROVENANCE.json).
The helper never executes the EXE or its MSIs. It parses embedded CAB containers
as data and uses Windows `expand.exe`; no system installation is performed.

| DLL | SHA-256 |
| --- | --- |
| `msvcp140.dll` | `7c26614e1d733892c2deac7e245ce115504b1d80592dd0a01b08e3e5a55f89ca` |
| `vcruntime140.dll` | `d1f4225df2cd877dbf130d5668a021dce3f94118455ff5ec952061c30afc9ce7` |
| `vcruntime140_1.dll` | `a7146c08f89fe5b04541ab507cdb59ff7b44534d4ba3c668a426c6450a03434e` |

All three are x64, version 14.51.36247.0, signed by Microsoft Windows Software
Compatibility Publisher / Microsoft Corporation. Their normal and delay
Microsoft-runtime dependencies close over these same three files. Windows
10/11 supplies UCRT/API-set implementations; those copies are omitted.

The original wheel's GLFW DLL required VC11. Its replacement is built from
unchanged GLFW 3.3.2 with VS2019 /MD, retaining Win32/WGL/EGL/OSMesa support.
Its zlib license remains separate. No ProcGen engine/assets are changed.
See `docs/licensing/MICROSOFT-RUNTIME.md` for reproduction and validation.
The download EXE is a local build input, excluded from binary/source archives.
