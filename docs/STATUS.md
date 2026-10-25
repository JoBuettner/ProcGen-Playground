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
- Initial configuration tests passed (37), runner tests passed (5), and strict
  mypy passed for all six source modules. Final complete suite still to run.
- PyInstaller built a windowed, folder-based standalone EXE with its own Python
  runtime, native libraries, assets, GLFW library, gym3 font/header, and notices.
- Agent inspected the packaged CoinRun window on the actual desktop, observed
  normal rendering, toggled its original `O` overlay shortcut, and closed it.
  The application log recorded successful termination. A user check of packaged
  movement/jump and double-click startup has been requested.
- Unicode extraction initially failed. Fixed by passing the asset-root option
  as UTF-8 bytes, avoiding gym3's string byte-count bug. No upstream files patched.
- Packaged native parity comparison is running against the 96 upstream cases,
  after ZIP extraction to a space/non-ASCII path and with Python/environment
  overrides removed. Do not treat this in-progress run as passed.

## Remaining gates and deferred work

- **No clean Windows machine/VM without Python has been tested.** Stripping PATH
  and overrides on this development host does not establish that release gate.
- Representative original CaveFlyer and Heist/Maze keyboard controls remain
  unchecked; their native configuration/stepping checks passed.
- GUI agent/human view switching and visual toggles need manual validation.
- Finish packaged parity checks, final unit tests, review, and build records.
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
