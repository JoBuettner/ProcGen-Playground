# Project status

Updated: 2026-10-30. Application version: **0.2.0**.

## Implemented

- Windows portable launcher for all 16 original ProcGen environments.
- Easy/Hard, level seed, Human/Agent observation and upstream visual options.
- Play/Stop/Exit, owned game-process cleanup, validation and per-user logs.
- Original ProcGen engine, assets, controls and game mechanics preserved.
- Portable binary/source ZIPs with checksums, licenses, credits and source/relink materials.
- GitHub-hosted Windows checks, packaging and automatic development prereleases
  on pushes to `main`. Publication runs separately and can be retried without
  rebuilding successful artifacts.

Hosted builds and automatic prerelease publication have completed successfully
(maintainer confirmed). The version 0.2.0 documentation/metadata update will
produce its own build after pushing; earlier binaries still have their earlier
version labels. Routine main-branch builds remain marked as prereleases.

## Automated verification

- Unit suite: **112 tests passed**; strict mypy passed for 10 source modules.
- Original native verification: **96 cases**, covering all games, difficulties
  and observation modes, including simplified visuals.
- Frozen native parity: **96 cases** matched the original package; **1,290**
  ProcGen data files matched upstream bytes.
- Artifact verification covers binary/source pairing, source and native file
  hashes, notice inclusion, controlled CRT provenance and runtime compatibility.
- Release failure tests cover transient/persistent server errors, recovery of
  drafts created despite an error, validation failures, and published-release
  and commit-target protection.

CI output and each release's checksums identify the exact corresponding build.
Local evidence from 2026-10-25 and 2026-10-28 is retained under
[verification/](verification/) as historical records, not descriptions of every
later release. The redistribution materials are documented in
[licensing/REDISTRIBUTION.md](licensing/REDISTRIBUTION.md).

## Recorded manual coverage

Earlier development-PC checks covered CoinRun controls, CoinRun/Heist/Cave Flyer
rendering, menu return, Stop, parent-close cleanup, selected settings, invalid
seed feedback, no console and a path containing spaces/non-ASCII characters.
The README screenshot shows the actual packaged launcher.

A completed final 16-game walkthrough and a separate-PC test without Python
have not been recorded in this repository. Automated verification does not
establish manual gameplay or clean-machine acceptance.
See the precise remaining scenarios in
[verification/DESKTOP-CHECKLIST.md](verification/DESKTOP-CHECKLIST.md).

## Release handling

Use the four assets produced together by a successful hosted run. Keep the
corresponding-source download accessible alongside each binary version and
retain its component notices. A normal release can be selected manually;
[RELEASING.md](RELEASING.md) describes the steps and evidence checklist.
An installer is outside the agreed scope. No required UI feature is known to
be missing.
