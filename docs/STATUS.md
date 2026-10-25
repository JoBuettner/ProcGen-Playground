# Development status

Last updated: 2026-10-25. This is a development build, not a public release.

## Milestones

- [x] M0 feasibility gate: original CoinRun playable on this Windows desktop
- [ ] M1: standalone portable CoinRun executable verified on a clean desktop
- [ ] M2: launcher and all 16 games
- [ ] M3: hardening and reproducible Windows build
- [ ] M4: installer and public release

## Verified evidence

- Initialized local Git repository; original plan committed as `61ed086`.
- Host has CPython 3.10.1, 64-bit AMD64 on Windows
  (`Windows-10-10.0.26200-SP0` reported by Python).
- Created project-local `.venv`; no global Python packages changed.
- Selected upstream ProcGen 0.10.7; PyPI supplies a CPython 3.10 Windows x64 wheel.
- Installed unmodified ProcGen 0.10.7, gym3 0.3.3, NumPy 1.26.4 and pinned
  build tools. All exact archive hashes are recorded in the lock files.
- Native `env.dll` loads; benchmark observations are `(1, 64, 64, 3)` and
  human frames are `(512, 512, 3)`.
- Original command `python -m procgen.interactive --env-name coinrun --level-seed 42`
  opened a game window. **The user confirmed display and keyboard controls
  worked**, then closed it; process exited successfully.
- `scripts/verify_upstream.py`: **96/96 passed**, covering all 16 games,
  easy/hard, agent/human views, simplified visuals, seed 42, stepping, key-to-action
  mapping, save/load state roundtrip, and environment closure. See the committed
  `docs/verification/upstream-smoke-2026-10-25.json` report. This is native testing,
  not a claim of playing every game with a keyboard.
- Fresh `.artifacts/lock-env` installation succeeded **offline**, using hashed
  archives, pinned bootstrap tools, and `--no-build-isolation`; `pip check` passed.
- Full unit suite: **42 passed**. Strict mypy passed for all six source modules.
  These also passed using the fresh offline-installed environment.
- PyInstaller built a windowed, folder-based standalone EXE with its own Python
  runtime, native libraries, assets, GLFW library, gym3 font/header, and notices.
- Agent inspected the packaged CoinRun window on the actual desktop, observed
  normal rendering, toggled its original `O` overlay shortcut, and closed it.
  The application log recorded successful termination. **The user also confirmed
  the packaged EXE starts by double-click, movement/jump work, and no console
  appears.**
- Unicode extraction initially failed. Fixed by passing the asset-root option
  as UTF-8 bytes, avoiding gym3's string byte-count bug. No upstream files patched.
- Packaged native parity comparison: **96/96 passed**, after ZIP extraction to
  a space/non-ASCII path with Python/environment overrides removed. All **1,290**
  bundled ProcGen data files match upstream bytes. The PE subsystem is Windows GUI.
  This automated report does not test GLFW window creation/keyboard input from
  that extraction path; the separate desktop check below supplies that evidence.
- Agent launched the ZIP-extracted application from
  `.artifacts/Portable Prüfung h90y2_i5/ProcGenPlayground/`, observed normal
  CoinRun rendering, verified the `O` keyboard overlay toggle, and closed it.
  Logs recorded successful shutdown; subsequent window inventory was empty.
- Independent standards review found no actionable violations or smells. Spec
  review found no correctness violations and called out the separate Unicode
  path desktop check. See `docs/verification/REVIEW.md`.
- Development ZIP: **84,309,452 bytes (80.4 MiB)**; application folder:
  **184,219,869 bytes (175.7 MiB)**. SHA-256:
  `040926ea82365d556930be37ce4ee1f6be92043097f2dac2d39bf22a14ec4364`.
  Committed frozen report: `docs/verification/frozen-smoke-2026-10-25.json`.
- A final end-to-end build-script run in the fresh environment passed `pip
  check`, all 42 tests, type checking, and notice collection. It was interrupted
  during the upstream native matrix after the user stopped Computer Use with
  Escape. It did not replace the previously validated portable ZIP. The script
  as a whole is therefore **not yet recorded as successfully executed**.

## Remaining gates and deferred work

- **No clean Windows machine/VM without Python has been tested.** Stripping PATH
  and overrides on this development host does not establish that release gate.
- Representative original CaveFlyer and Heist/Maze keyboard controls remain
  unchecked; their native configuration/stepping checks passed.
- GUI agent/human view switching and visual toggles need manual validation.
- Complete an uninterrupted `scripts/build_windows.ps1` run. Individual native,
  packaging, parity, and unit/type commands have passed as recorded above.
- Missing-library GUI error handling has unit coverage, but the desktop error
  dialog check was stopped before verification; the temporary DLL rename in a
  disposable extraction was restored. No failure-dialog pass is claimed.
- Native Qt/C++ redistribution compliance audit remains open. Asset notices and
  installed distribution/Python/Tcl/Tk license files are collected and bundled.
- GitHub remote is not configured. No public release or installer exists, and
  CI has not run on GitHub. A local workflow is not evidence of CI success.
- Per the plan, the polished M2 launcher and M4 installer/publication wait for
  the standalone gate. CLI options/configuration are minimal M1 test support.

## Failures and resolutions

- Sandbox DNS 11001: dependency downloads required network permission.
- Git index writes required permission to the repository's `.git` directory.
- Unused setuptools vendored runtime hook crashed the first frozen build:
  collect only runtime package data/native libraries and exclude build tooling.
- Non-ASCII asset roots were truncated by gym3 0.3.3's str-option length:
  use its existing bytes-option support, preserving the exact path and assets.
- Sandbox pip metadata rename failed with WinError 5: use a project-local
  TEMP/TMP directory for the fresh offline installation.
- Windows computer-use policy blocks python.exe window inspection. Original
  CoinRun gameplay was verified by the user; the packaged executable was
  inspectable with computer-use tools.
