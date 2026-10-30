# Windows build

## Tested development target

Windows x64, CPython **3.10.1 AMD64**, ProcGen **0.10.7**, NumPy **1.26.4**,
gym3 **0.3.3**, PyInstaller **6.16.0**. The local OS reports
`Windows-10-10.0.26200-SP0` through Python; this platform string is not a claim
that Windows 10 specifically was tested. The Python launcher (`py -0p`) did not
discover the existing interpreter, so the commands use `python` directly.

ProcGen wheel: `procgen-0.10.7-cp310-cp310-win_amd64.whl`.
The upstream tag `0.10.7` resolves to commit
`5e1dbf341d291eff40d1f9e0c0a0d5003643aebf`.
The ProcGen engine, Python packages and game assets remain unmodified.
The native GLFW viewer is rebuilt from the same unmodified 3.3.2 source with
VC14 to remove its separate VC11 redistribution dependency.

## Set up

Use a Windows x64 CPython 3.10 installation; 3.10.1 is the recorded build patch.
The lock is specific to this interpreter family and platform.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-bootstrap.lock
.\.venv\Scripts\python.exe -m pip install --require-hashes --no-build-isolation -r requirements-windows.lock
```

The bootstrap pins pip/setuptools/wheel before gym's source distribution is
built. All other dependencies have prebuilt wheels. `--no-build-isolation`
keeps gym's build on those pinned tools. The complete inventory and downloaded
archive hashes are in `requirements-windows.txt`, `requirements-windows.lock`,
and `docs/DEPENDENCY_ARTIFACTS.json`.

For offline setup, first download artifacts on a networked build machine with
`pip download --no-deps -r requirements-windows.txt -d wheelhouse`, then add
`--no-index --find-links wheelhouse` to **both** install commands. An offline
installation into a fresh environment was verified on 2026-10-25. Archive input
hashes are pinned; bit-for-bit identical generated wheels/EXEs/ZIPs are not
claimed (build tools and timestamps can affect them).

## Verify and build

Packaging requires Visual Studio 2022 or 2019 with its CMake component,
v142 C++ tools, Windows SDK **10.0.19041.0**, and the pinned official x64 VC14
runtime package. GitHub's `windows-2022` image supplies VS2022 Enterprise and
these build tools. Local builds fall back to VS2019 when VS2022 CMake is absent.
The project's documented Microsoft redistribution terms remain applicable;
the build worker does not need a separate Community IDE installation.
The selected runtime must be at least as recent as the newest runtime-dependent
MSVC toolset in the bundle. The exact runtime hashes, entitlement route and
same-version GLFW build are documented in
`licensing/MICROSOFT-RUNTIME.md`. The build fails if those inputs are absent;
it does not substitute DLLs from ambient PATH caches or install system runtimes.

```powershell
.\scripts\build_windows.ps1
```

The script fails on an unsuccessful native command. It checks Python, package
consistency, unit tests, types, licenses, and all 96 original-package native
cases; verifies/downloads pinned source archives at build time; stages the
controlled CRT and rebuilds GLFW; builds the windowed executable; creates both
the portable ZIP and actual corresponding-source companion with checksums;
verifies source/binary pairing, notice coverage and native-file provenance;
then extracts it into a directory containing spaces and non-ASCII characters
and compares 96 packaged cases against the upstream results.

Outputs:

- `dist/ProcGenPlayground/ProcGenPlayground.exe` and its adjacent `_internal/`
- `dist/ProcGenPlayground-Windows-x64-portable.zip`
- `dist/ProcGenPlayground-Windows-x64-portable.zip.sha256`
- `dist/ProcGenPlayground-corresponding-sources.zip`
- `dist/ProcGenPlayground-corresponding-sources.zip.sha256`
- `.artifacts/license-bundle-verification.json`
- `.artifacts/upstream-smoke.json` and `.artifacts/frozen-verification.json`

The source companion contains actual pinned archives, this project's source,
notices and rebuild/relink instructions. The prepared local companion also
includes verified OpenBLAS application objects. A fresh clone can build the
complete source-only companion without those optional generated objects;
`scripts/package_sources.py` rejects a partial or hash-mismatched object set.
To recreate the faster object shortcut, follow
`licensing/numerical-relink/README.md`; compiler binaries are obtained separately.
No source or toolchain is downloaded or compiled during gameplay.

GitHub Actions runs both jobs on GitHub-hosted `windows-2022` machines.
Pushes and pull requests run the source checks. Every push to `main` also builds
the portable ZIP/source companion and publishes a development prerelease after
verification passes. Its unique tag contains the app version and commit SHA,
for example `v0.2.0-g0123456789ab`. Both ZIPs and checksum files are release
assets; launch instructions and the third-party notice are added automatically.
Published releases are not overwritten on reruns. Publishing is a separate job
that downloads the verified build artifact. After a publishing failure, use
**Re-run failed jobs** to retry just that job without rebuilding the app.
Draft creation retries HTTP 500/502/503/504 up to three times with a release
lookup between attempts; other errors fail immediately. Draft upload and
publication are separate, so partial drafts can be resumed safely.
**Run workflow → main** also supports
manual runs. Other branches and pull requests cannot run the release job.
No self-hosted runner or extra secrets are needed; only the release job gets
`contents: write` permission through the automatic GitHub token.
Build diagnostics are uploaded even when packaging fails. Hosted packaging and
automatic prerelease publication have both completed successfully, as confirmed
by the maintainer. Each new release's workflow records its own verification.

Native verification strips Python, virtual-environment, GLFW, and GLContext
environment overrides; PATH contains only Windows System32. It checks that
the PE subsystem is Windows GUI and that all bundled ProcGen data files match
the installed originals. This is useful isolation, **not a clean-machine GUI
test**. Desktop checks are tracked separately in `STATUS.md` and `RELEASING.md`.

## Run from source

Before creating a polished launcher, validate original interactive ProcGen:

```powershell
.\.venv\Scripts\python.exe -m procgen.interactive --env-name coinrun --level-seed 42
```

For the wrapper, in this PowerShell session:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -m procgen_playground
```

Developer options are `--game`, `--difficulty easy|hard`, `--vision human|agent`,
`--level-seed`, `--disable-backgrounds`, `--restrict-themes`, and `--monochrome`.
No arguments opens the launcher with CoinRun, hard mode, normal visuals, and
human view selected. The internal `--run-game` mode opens the selected original
interactive game directly; the launcher uses the same packaged EXE for this
child, never an external Python installation. Source development uses the same
interpreter with `-m procgen_playground` and an explicit source path.
The internal `--verify-engine REPORT_JSON` mode runs a finite native check
without a game window; its deterministic RNG seed is used only for diagnostics.

The launcher allows a single instance per user with an OS-backed file lock.
Gameplay runs in one child process. A Windows kill-on-close Job Object owns the
child; normal launcher closure terminates and reaps it, and the job is also a
backstop if the launcher exits unexpectedly after assigning the child.

Empty/unset level seed leaves ProcGen's unlimited procedural generation
defaults. A seed selects `start_level=seed, num_levels=1`. It does not by itself
fix every random choice or promise an identical complete gameplay trajectory.

## Compatibility and packaging findings

1. Sandbox dependency download initially failed with DNS error 11001. Network
   permission resolved it; no dependency is downloaded during gameplay.
2. ProcGen ships `data/prebuilt/env.dll` and `data/assets`. The DLL statically
   links Qt; its PE imports also require Visual C++ runtimes. PyInstaller
   collects the runtime DLLs into `_internal`; clean-machine loading still
   needs desktop verification.
   The original audit is in `LICENSE-AUDIT.md`; completed source/notices/runtime
   preparation is documented in `licensing/REDISTRIBUTION.md`. MIT on the
   launcher does not replace dependency distribution requirements.
3. The visible upstream game window uses gym3's GLFW/OpenGL 3.3 renderer, which
   dynamically loads GLFW and ModernGL. `gym3/internal/font.bin` and `libenv.h`
   are required alongside its Python code.
4. Initially collecting every submodule also collected unused build tooling.
   A setuptools vendored `backports` import crashed a PyInstaller runtime hook.
   The spec now collects package data/native libraries and required dynamic
   modules explicitly and excludes setuptools/pkg_resources. Runtime uses
   CFFI ABI mode and never needs compilation.
5. **Unicode paths:** gym3 0.3.3's `CEnv._convert_options` encodes str values as
   UTF-8 but supplies `len(str)`, truncating non-ASCII native options. The
   wrapper passes the original absolute asset directory as UTF-8 **bytes**
   (including its trailing separator). gym3's existing bytes handling supplies
   the correct length. There is no game-engine patch or copied asset cache.
   Tests cover this mapping; frozen verification checks output parity.
6. Gym emits its upstream maintenance notice. It is logged; NumPy remains
   pinned below 2.0. The wrapper does not replace Gym/ProcGen implementations.
7. The local Python installation omitted standalone Tcl/Tk notices, so the
   original 8.6.12 notices were fetched from the corresponding upstream tags
   and retained in `third_party/`. Python's own license is copied at build time.
8. One sandbox pip attempt failed to atomically replace generated metadata in
   its redirected temporary directory (WinError 5). Setting TEMP/TMP to a
   project-local directory resolved it. This was not a dependency resolution
   failure.

## Sources

- [ProcGen 0.10.7](https://pypi.org/project/procgen/0.10.7/)
- [Pinned interactive interface](https://github.com/openai/procgen/blob/0.10.7/procgen/interactive.py)
- [Pinned environment and asset paths](https://github.com/openai/procgen/blob/0.10.7/procgen/env.py)
- [gym3 C option conversion](https://github.com/openai/gym3/blob/master/gym3/libenv.py)
- [PyInstaller spec files](https://pyinstaller.org/en/v6.16.0/spec-files.html)

Installed wheel contents are the authority for implementation and parity tests.
