# Development status

Last updated: 2026-10-28. This is a development build, not a public release.

## Milestones

- [x] M0 feasibility gate: original CoinRun playable on this Windows desktop
- [x] M1: standalone portable CoinRun executable verified on the current PC
- [x] M2: launcher implementation and all 16 game selections
- [ ] Final acceptance: full 16-game desktop play/close/relaunch walkthrough
- [ ] M3: hardening and reproducible Windows build
- [ ] M4: final validation and portable public release (no installer)

## Verified evidence

**Updated sequencing agreed with the user:** the successful gameplay test was
on the current PC. Full desktop acceptance and separate-PC / no-Python
verification are deferred until final release validation. Development continues
without those checks blocking it. The portable ZIP is the chosen distribution;
an installer is out of scope. This
overrides the original plan's clean-machine prerequisite for moving past M1.
It does not mean that the separate-PC test has passed.

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
- Current version: **0.2.0.dev0**. Full unit suite: **103 passed**. Strict mypy
  passed for all **10** source modules, using the fresh offline-installed
  environment. Tests include actual Windows child/process ownership and abrupt
  owner-exit cleanup, plus frozen/development argument roundtrips for all games.
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
  `.artifacts/Portable PrÃ¼fung h90y2_i5/ProcGenPlayground/`, observed normal
  CoinRun rendering, verified the `O` keyboard overlay toggle, and closed it.
  Logs recorded successful shutdown; subsequent window inventory was empty.
- Independent standards review found no actionable violations or smells. Spec
  review found no correctness violations and called out the separate Unicode
  path desktop check. See `docs/verification/REVIEW.md`.
- Historical launcher ZIP after the 2026-10-25 initial audit: **63,368,622 bytes (60.4 MiB)**;
  application folder: **122,823,859 bytes (117.1 MiB)**. SHA-256:
  `0ade817ee1abdcd9d19dc293ac4392bace40c813167b410db1d5c5e1ee2de19b`.
  Historical frozen report: `docs/verification/frozen-license-2026-10-25.json`:
  **96/96 passed**, 1,290 original files unchanged, supplemental notices present,
  FFmpeg absent. Older frozen reports record historical M1/M2 builds.
- License-audit rebuild: 85 tests, strict mypy, notice collection, PyInstaller,
  ZIP generation and all 96 frozen parity cases passed. Native binary hashes,
  import evidence and source categories are recorded in
  `docs/verification/bundled-license-audit-2026-10-25.json`. Build/verification
  logs are `.artifacts/license-build.log` and `.artifacts/license-frozen-final.log`.
  That historical native manifest recorded 45 Microsoft DLLs from the builder's
  ambient cached runtime directory. The current build replaces that selection
  with three controlled, signed VC14 runtime files and same-version rebuilt GLFW.
- **Complete build script passed** using `.artifacts/lock-env`: package
  consistency, 85 tests, types, notices, 96 original native cases, PyInstaller,
  ZIP/checksum generation, and 96 frozen parity cases. Full local log:
  `.artifacts/m2-build.log`. The earlier interrupted attempt is superseded.
- Packaged launcher desktop checks passed for CoinRun play/close/return,
  invalid-seed feedback, Heist seed 42 with agent view/monochrome, and closing
  the parent while its game runs. Final rebuild also passed Stop-game cleanup,
  Cave Flyer startup/render/close/return, and upstream output capture in game.log.
  These are representative checks, not a completed 16-game desktop matrix.
- Separate standards/spec reviews of `0948979...70f6b65` found no actionable
  findings. Details: `docs/verification/M2-LAUNCHER.md`.

## Current licensing build — 2026-10-28

The corrected VC14 14.51 build passed 103 unit tests, strict mypy, 96 original
native cases and 96 frozen parity cases; 1,290 original data files are unchanged.
The binary/source pair includes 11 pinned source archives and nine verified
numerical relink inputs. All 54 native files have recorded provenance; runtime
exports and observable toolset floors pass. See `verification/LICENSE-COMPLIANCE.md`
and `verification/frozen-licensing-2026-10-28.json`.
Portable ZIP SHA-256: `07aab507a22141335beee0307c438d1ee037e577294227705e9974b3857957ef`.

## Remaining gates and deferred work

- **No clean Windows machine/VM without Python has been tested.** Stripping PATH
  and overrides on this development host does not establish that release gate.
- Full 16-game menu acceptance and representative physical movement/shooting/
  rotation controls remain to check. See `docs/verification/DESKTOP-CHECKLIST.md`.
- Both views and a visual toggle were inspected on desktop; remaining setting
  combinations and duplicate-launcher message behavior need final manual checks.
- Missing-library GUI error handling has unit coverage, but the desktop error
  dialog check was stopped before verification; the temporary DLL rename in a
  disposable extraction was restored. No failure-dialog pass is claimed.
- License/source preparation now supplies actual pinned sources, original
  notices, Qt and libquadmath rebuild/relink helpers and tested replacement
  procedures, Qt subcomponent attribution inventory, and controlled Microsoft
  runtime provenance/terms. The matching source companion must be published
  alongside each binary release. See `licensing/REDISTRIBUTION.md`; the initial
  `LICENSE-AUDIT.md` is historical.
- GitHub remote is configured and `main` tracks `origin/main`. The user confirmed
  hosted source checks passed. Packaging now targets GitHub-hosted Windows;
  its first complete run after this configuration change remains to verify.
- The M2 interface/process implementation is complete and packaged. Remaining
  work is final acceptance and publication of the paired binary/source materials.
  There is no known missing required UI feature. Unchecked UI scenarios are
  listed precisely in `docs/verification/DESKTOP-CHECKLIST.md`.

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
