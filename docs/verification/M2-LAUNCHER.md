# Launcher development verification (2026-10-25)

## Scope and sequencing

The user confirmed the prior portable test was on the current development PC
and explicitly moved testing on another PC to the end. Launcher development
therefore proceeds without representing clean-machine validation as complete.

Version: `0.2.0.dev0`. No upstream ProcGen files or native mechanics are modified.

## Implemented

- Catalog of all 16 standard games, readable names, and concise descriptions.
- Easy/hard (hard default), optional validated seed, human/agent view, and the
  three supported visual options. No seed leaves native level generation alone.
- Keyboard navigation and Play/Stop/Exit accelerators; original game shortcuts.
- One launcher per user via OS-backed file lock, one game child at a time.
- Frozen child command uses the same executable with internal `--run-game`;
  development uses the running interpreter and explicit source module path.
- Separate rotating launcher/game logs in per-user AppData.
- Launcher closes/reaps its child. A kill-on-close Windows Job Object also
  stops an assigned child after unexpected owner termination.
- Selections remain in the current launcher session. No saved preferences yet.

## Desktop checks performed on the current PC

- Packaged launcher opens with CoinRun / Hard / Human and standard visuals.
  Layout inspected at the host's display scaling; all controls/footer visible.
- Play opens original CoinRun in a separate window; launcher remains responsive
  with Play disabled and Stop enabled.
- Closing CoinRun returns to the menu, updates status, and re-enables Play.
- Select Heist: title and one-sentence description update correctly.
- Enter `not a seed` and press Play: readable inline validation, no game launch.
- Correct seed to `42`, choose Agent observation and Monochrome assets, then
  Play: Heist renders in the selected view with simplified assets. Child log
  confirms exact validated options.
- Close the launcher while Heist runs: launcher logs closure; the recorded
  child PID no longer exists. No orphan game process was observed.

## Automated checks

- All game IDs and full option sets round-trip through frozen/development child
  commands; frozen commands never invoke an external Python.
- Tests cover duplicate-child prevention, launch failure cleanup, child exit
  reporting, launcher/runner dispatch, and nonmodal child failure reporting.
- Actual Windows process tests cover child termination on Job Object closure,
  normal session shutdown, and abrupt owner termination.
- New launcher ZIP passed **96/96 native parity cases**, from a space/non-ASCII
  extraction path with stripped Python/environment overrides; all **1,290**
  ProcGen data files matched the upstream installed package.

## Remaining desktop/release checks

- Launch/play/close/relaunch all 16 games through the final packaged menu.
  Native tests for all 16 do not replace this complete desktop checklist.
- Confirm representative shooter/rotation controls, Stop, duplicate launcher
  feedback, and full menu keyboard navigation on the final build.
- Separate-PC / no-Python, antivirus/SmartScreen, and final distribution
  licensing checks remain final-release work.
