# ProcGen Playground

Play the original 16 ProcGen games through an independent Windows desktop app.
This project is not an official OpenAI product.

**Development / prerelease:** the current M1 build opens CoinRun directly.
A game-selection launcher is planned after standalone packaging is validated.
Clean-machine GUI verification is still required; see [status](docs/STATUS.md).

## Play a development portable build

1. Extract the entire `ProcGenPlayground-Windows-x64-portable.zip`.
2. Open the extracted `ProcGenPlayground` folder.
3. Double-click `ProcGenPlayground.exe` to open CoinRun.
4. Close the game window to quit.

You do not need Python, a terminal, or an internet connection to play.
Requirements: Windows x64, AVX-capable processor, and an OpenGL 3.3 graphics
driver. Upstream documents Windows 10; additional Windows versions need testing.
Local build artifacts are under `dist/`; no public downloads are available yet.

## Controls

ProcGen's original controls are preserved: arrow keys and Q/W/E/A/S/D perform
game-dependent actions. CoinRun uses left/right to move and up to jump.
`O` toggles the upstream information overlay. `Shift+F1` saves the current state
in memory; `F1` reloads it during the same session. The score appears in the
upstream overlay. See the [upstream game descriptions](https://github.com/openai/procgen#environments).

## Troubleshooting

Startup failures show a dialog when possible. Logs are stored per user at
`%LOCALAPPDATA%\ProcGenPlayground\logs\playground.log`, with bounded rotation.
Extract all files together; do not move the executable away from `_internal`.
The app never downloads dependencies or compiles the engine at runtime.

## Development

Use Windows x64 and CPython 3.10. Follow [BUILD.md](docs/BUILD.md) for the pinned
dependencies, tests, and portable build. The full roadmap is in
[the implementation plan](PROCGEN_PLAYGROUND_CODEX_PLAN.md).

The engine, timing, controls, and assets come from unmodified `procgen==0.10.7`.
The wrapper is MIT licensed; upstream code, assets, and dependencies have their
own terms. Read [attributions](docs/ATTRIBUTION.md) before redistribution.
