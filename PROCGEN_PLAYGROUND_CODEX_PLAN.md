# ProcGen Playground: Codex Implementation Plan

> **Scope/sequencing update, 2026-10-25 (user decision):** distribute the portable
> ZIP only; no installer is needed. Full desktop acceptance of all games and
> the separate-PC/no-Python test happen at the end of development. These decisions
> override installer work and earlier clean-machine milestone prerequisites below.
> Current progress: `docs/STATUS.md`; dependency obligations: `docs/LICENSE-AUDIT.md`.

## 1. Project brief

Build **ProcGen Playground**, an independent, open-source desktop application that lets nontechnical users play the original 16 [OpenAI ProcGen](https://github.com/openai/procgen) games without installing Python, opening a terminal, or compiling anything. Start with **Windows x64** and distribute a portable ZIP containing an executable that can be launched by double-clicking. After that works, add a friendly launcher, an optional Windows installer, and automated GitHub releases. A browser version is a possible later project, not part of the current scope.

**Primary principle:** Wrap and redistribute the original environments; do not change their game mechanics, levels, rewards, physics, or action semantics. Keep ProcGen scientifically comparable to its original implementation.

### Deliverables

- A public-ready GitHub repository with a documented, reproducible build
- A Windows portable release: extract ZIP and double-click `ProcGenPlayground.exe`
- All 16 original games playable using the existing interactive controls
- A launcher for choosing a game and supported options (once the executable is working)
- Packaged native libraries, game assets, Python runtime, and required dependencies; no Python installation on the user's machine
- Automated tests/build checks, a manual release-validation checklist, appropriate license/asset attributions, and a useful README
- Later: an installer and tagged release automation

### Out of scope initially

- Browser/WebAssembly port, multiplayer, online accounts, leaderboards, custom game logic, AI agents, reinforcement learning training features, gamepad support, and modifying ProcGen itself
- Supporting every desktop operating system in the first release
- Extensive redesign of the actual ProcGen game window

## 2. Verified upstream facts and starting references

- Upstream: https://github.com/openai/procgen
- Interactive interface: https://github.com/openai/procgen/blob/master/procgen/interactive.py
- Game names, actions, native-library/asset paths, environment options: https://github.com/openai/procgen/blob/master/procgen/env.py
- Installation and supported systems: https://github.com/openai/procgen/blob/master/README.md
- Code license: https://github.com/openai/procgen/blob/master/LICENSE
- Asset licenses: https://github.com/openai/procgen/blob/master/ASSET_LICENSES.md
- PyInstaller: https://pyinstaller.org/en/stable/

At the time this plan was written, upstream documentation lists Windows 10, 64-bit Python 3.7–3.10, and an AVX-capable CPU. Use **Python 3.10 x64** as the initial build target, verify it works, and pin the working dependencies. The engine is compiled C++ with Qt and is loaded by Python through `gym3`; the installed package expects native binaries under `procgen/data/prebuilt` and resources under `procgen/data/assets`. Do not assume a simple `pyinstaller launcher.py` command will collect those correctly.

The original interactive module exposes game, distribution mode, fixed level seed, agent/human view, and flags such as disabling backgrounds, restricting themes, and using monochrome assets. Defaults include `distribution_mode='hard'` and `vision='human'`. The standard benchmark has these 16 game names:

`bigfish`, `bossfight`, `caveflyer`, `chaser`, `climber`, `coinrun`, `dodgeball`, `fruitbot`, `heist`, `jumper`, `leaper`, `maze`, `miner`, `ninja`, `plunder`, `starpilot`.

Important: `coinrun_old` exists as a legacy option in the interactive script but is **not** one of the standard 16 games. Do not include it in the primary list.

## 3. Codex execution rules

1. **Implement, test, and document**, rather than just proposing designs. Work through milestones in order; keep a concise progress checklist in `docs/STATUS.md`.
2. **Validate assumptions against upstream source and installed packages** before implementing. Pin an explicit ProcGen release/version (and any upstream commit if source modifications are unavoidable).
3. **Do not modify game behavior.** If upstream compatibility patches are essential, keep them minimal and isolated, explain why, and add regression tests where possible. Avoid copying/forking the full engine unless necessary.
4. **Prioritize a working portable binary over cosmetic polish.** Stop expanding scope if packaging is not verified.
5. **Be truthful about verification.** Never mark Windows GUI behavior as tested if only a headless environment was available. Record commands run, their outcome, outstanding blockers, and manual checks remaining.
6. Avoid `shell=True`, downloading dependencies at runtime, hidden terminal requirements, and storing user data in the installed program folder.
7. Keep the project maintainable: small modules, type hints, testable configuration/argument mapping, and minimal dependencies.
8. If a step is blocked, document the exact failure and implement the next independently testable task. Do not silently replace original ProcGen with a different game implementation.

## 4. Milestones and tasks

### M0: Feasibility spike and dependency lock (must complete first)

- [ ] Create an isolated **Windows x64 / Python 3.10** development environment.
- [ ] Pin an upstream ProcGen version and dependencies; inspect published wheel availability and compatibility.
- [ ] Get the unmodified interactive mode running locally for `coinrun` using the real upstream package.
- [ ] Test another game with different controls, such as `caveflyer`, plus `heist` or `maze`.
- [ ] Check that `procgen` native binaries (`env.dll` on Windows), Qt runtime dependencies, and all resource files are located correctly.
- [ ] Test `human` view and `agent` view, and at least one fixed level seed and visual simplification setting.
- [ ] Document exact installation steps, versions, errors and workarounds in `docs/BUILD.md` and `docs/STATUS.md`.
- [ ] Decide whether direct use of the pinned upstream package works. Investigate forks or compatibility fixes **only** if necessary, and verify environment fidelity before switching.

**Gate:** The original game is actually playable in an unpackaged Windows development environment. If this is not established, do not build a polished frontend yet.

### M1: Minimal standalone Windows application (v0.1)

- [ ] Implement the smallest executable entry point that launches the original interactive `coinrun` game **without requiring an external `python` process or terminal**.
- [ ] Use PyInstaller **onedir** mode initially. Package the interpreter, Python dependencies, `procgen` shared library, asset directories, and necessary native/Qt libraries. Add a maintained `.spec` file and/or PyInstaller hooks to handle package data and dynamically loaded libraries.
- [ ] Preserve the runtime paths expected by `procgen.env` instead of relocating assets arbitrarily.
- [ ] Verify the built `.exe` works when launched by double-clicking, with **no console window** and without developer-only environment variables.
- [ ] Verify it launches from an arbitrary extracted location, including a path containing spaces and non-ASCII characters.
- [ ] Verify that no Python installation is necessary. Test on a clean Windows VM or equivalent separate machine when possible.
- [ ] Package the application folder as `ProcGenPlayground-Windows-x64-portable.zip`.
- [ ] Report application size and include user-friendly handling/logging for missing native libraries and startup failures.

**Gate:** A user can unzip the release and play CoinRun by double-clicking an executable on a clean supported Windows system.

### M2: Usable launcher and all 16 games (v0.2)

Use a simple, dependable graphical user interface, such as Tkinter, unless M0/M1 demonstrate that another toolkit is a better fit. Avoid heavy frontend frameworks unless justified.

**Minimum interface**

- [ ] A labeled dropdown/list for all 16 games, with human-readable names and one-sentence descriptions
- [ ] Clear **Play** button and **Exit** button
- [ ] Difficulty selection, initially `easy` and `hard` (default `hard`); expose `extreme` only if validated and clearly mark game-specific modes as such
- [ ] Optional integer **level seed** input: empty means normal procedural level generation; nonempty fixes `start_level` and `num_levels=1`
- [ ] View selection: **Human** versus **Agent observation** (explain that agent view corresponds to the benchmark's observation)
- [ ] Visual toggles: **Backgrounds**, **Restrict themes**, **Monochrome assets**. Use upstream defaults initially.
- [ ] Compact control instructions: arrow keys plus Q/W/E/A/S/D as applicable; link to per-game details, without inventing unsupported bindings
- [ ] Clear feedback for invalid settings and errors; readable labels and keyboard accessibility
- [ ] User can close the game window and return to the launcher to choose another game

**Process architecture**

Implement a testable `LaunchConfig` data structure and a game-runner module that calls the upstream interactive API. Preferred robust design: keep the Tkinter launcher responsive while gameplay runs in a **separate child process using the same packaged executable**, with an internal `--run-game` entry mode. In development mode this may use `sys.executable` with the project entry module. Use `subprocess.Popen([...], shell=False)`; **never invoke an externally installed `python` in the frozen app**. Handle PyInstaller's frozen executable semantics explicitly.

- [ ] Restrict parsed arguments and accepted game names/flags; keep configuration-to-upstream mapping in one module
- [ ] Handle child process exit, start failures and logs
- [ ] Prevent unintentional duplicate running instances, or provide a deliberate, understandable policy
- [ ] Ensure closing the launcher or game leaves no orphan processes
- [ ] Ensure game keyboard input reaches the game window
- [ ] Store optional user settings in a per-user application-data directory, not under the extracted program directory
- [ ] Preserve the original game controls, timing, scores, and save/load state behavior where supported
- [ ] Do not claim a fixed level seed guarantees an identical complete gameplay trajectory unless all relevant randomness has been verified; document the upstream seed semantics

**Gate:** Launch, play, close, and relaunch every one of the 16 environments from the packaged app. Native engine behavior matches the original interactive script under equivalent settings.

### M3: Testing and packaging hardening

- [ ] Unit tests for all 16 game IDs, config validation, defaults, CLI/process arguments, and option-to-upstream mapping
- [ ] Smoke test that initializes each environment with one instance, observes/steps it, and closes it without crashing
- [ ] Manual game-window test for representative control schemes: platformer, maze, shooter, plus every game's startup
- [ ] Compare representative observations and fixed-seed level behavior against an unmodified upstream installation with matching version/options; don't infer parity merely from a successful launch
- [ ] Test user scenarios: launch from ZIP extraction, no Python installed, close/reopen, change settings, invalid seed, failure to launch, path with spaces, repeated opening, and antivirus false-positive reporting
- [ ] Confirm no unwanted first-run download/compile operation is required
- [ ] Build on a Windows runner with GitHub Actions; run automated tests and build the ZIP. **Distinguish automated build success from GUI testing on a real desktop.**
- [ ] Capture dependency versions / hashes and document a reproducible local build
- [ ] Produce a release checklist in `docs/RELEASING.md`

**Gate:** Reproducible portable build plus documented evidence that it works on a clean Windows desktop.

### M4: Installer and public release (v1.0)

- [ ] Add an optional Windows installer using Inno Setup, built from the already validated portable application
- [ ] Installer provides Start Menu shortcut and straightforward uninstall; avoid administrator permissions unless required
- [ ] Ensure user settings survive uninstall/reinstall appropriately; do not silently delete user-created data
- [ ] Add app name, version information and an appropriate icon. Do not imply this is an official OpenAI product.
- [ ] GitHub Actions workflow builds portable ZIP and installer on a pinned Windows environment; publication on version tags is gated on successful tests and release validation
- [ ] Publish release notes, checksums, tested platforms, minimum requirements, download and launch instructions, and known limitations
- [ ] If code-signing is unavailable, document the possible Windows SmartScreen warning without suggesting that users turn off security protections
- [ ] Preserve upstream code notices and all relevant third-party license/attribution requirements, including assets under different licenses; document provenance and modification status

**Gate:** A nontechnical Windows user can download, install or unzip, find a game, and play it without technical setup.

## 5. Suggested repository layout

```text
procgen-playground/
├── src/procgen_playground/
│   ├── __init__.py
│   ├── __main__.py          # launcher/runner dispatch
│   ├── launcher.py          # desktop GUI
│   ├── game_runner.py       # original ProcGen interactive integration
│   ├── config.py            # validated game/options model
│   ├── games.py             # catalog of the 16 games
│   └── logging_utils.py
├── tests/
│   ├── test_config.py
│   ├── test_launch_args.py
│   └── test_game_catalog.py
├── packaging/
│   ├── procgen-playground.spec
│   └── windows-installer.iss
├── scripts/
│   └── build_windows.ps1
├── .github/workflows/
│   ├── windows-build.yml
│   └── release.yml
├── docs/
│   ├── BUILD.md
│   ├── STATUS.md
│   ├── RELEASING.md
│   └── ATTRIBUTION.md
├── LICENSE
├── README.md
└── pyproject.toml
```

Adjust the structure to fit actual implementation needs. Do not create empty placeholder modules merely to match the tree. Upstream licenses and notices may need to be bundled separately as well.

## 6. Definition of done for the first public release

A release counts as done only if all of the following are true:

1. The portable build is downloadable as a GitHub release asset.
2. A Windows x64 user with a supported AVX-capable processor can extract it and double-click the app, with no command line or Python installation.
3. The launcher exposes all 16 standard ProcGen environments, and all of them open and accept keyboard input.
4. The game settings match upstream behavior, with `hard` and standard visuals as defaults.
5. Game-window closure and subsequent launches work; the app provides comprehensible diagnostics if something breaks.
6. The necessary native binaries, assets, notices, and license files are included.
7. The build is reproducible, tests pass, and the README gives short usage instructions.
8. The release was tested on a clean Windows desktop, or is explicitly labeled **pre-release / GUI testing incomplete** until that verification occurs.

## 7. Future work: deliberately deferred

Once desktop distribution is stable, consider:

- Linux and macOS packaging with separate native build/test pipelines
- Improved navigation, game-specific control hints, screenshots, and optional gamepad input
- Research-oriented presets and comparisons (fixed seeds, controlled visual ablations, observation overlays, human-play recordings)
- A browser version, likely requiring a careful WebAssembly feasibility investigation rather than assuming a direct port of the Python/Qt interface

Keep browser concerns from complicating the first desktop app, but keep game selection and options separate from the GUI so they can be reused later.

## 8. First instruction to Codex

> Execute **M0 and M1 first**. Inspect the existing repository and upstream references, verify interactive ProcGen on Windows/Python 3.10, and produce a truly standalone Windows portable executable. Implement only the minimum necessary UI or launcher for this milestone. Keep `docs/STATUS.md` updated with what is verified versus untested. Once M1 passes, proceed to M2–M4 in order, committing coherent steps. Do not redesign ProcGen or claim release readiness without a successful clean-machine GUI test.
