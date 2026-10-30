# Release validation checklist

Current output is an M2 development artifact with the 16-game launcher.
Distribution uses the portable ZIP; an installer is out of scope. By user
decision, full desktop acceptance and separate-PC testing happen at the end.
Development prereleases are generated automatically; stable release acceptance
is tracked separately below.

## Automatic development releases

Pushing to `main` now runs checks, builds and verifies both ZIPs on GitHub-hosted
Windows, then publishes a prerelease with the four ZIP/checksum assets. Tags use
the app version plus commit SHA. Release notes include launch instructions and
the complete third-party notice. Reruns preserve published releases; incomplete
draft uploads can be retried. Manual **Run workflow → main** is also supported.
These automatic prereleases report automated validation only. Desktop testing
and a deliberately versioned stable release remain separately recorded steps.

## Automated evidence

- [x] Fresh Windows x64/Python 3.10 setup using hashed lock files (current host)
- [x] `scripts/build_windows.ps1` completed successfully for M2
- [x] Every environment initializes, observes, steps, restores state, and closes
- [x] Frozen outputs match unmodified upstream for all 96 native cases
- [x] Extracted data/native files match original package hashes
- [x] Space/non-ASCII extraction path and stripped environment tests pass
- [x] Development ZIP checksum, version, size, build log, dependency inventory recorded
- [ ] Repeat automated build/verification on the final release candidate
- [ ] GitHub Actions build actually executed and passed (a workflow file alone is insufficient)

## Real desktop checks (record OS, CPU/GPU, artifact SHA-256, date, tester)

- [ ] Clean supported Windows x64 machine with AVX and **no Python installed**
- [ ] Download/extract full ZIP and double-click EXE without a terminal
- [ ] Game renders, accepts keyboard input, and has no console window
- [ ] CoinRun, CaveFlyer, Heist/Maze representative controls verified
- [ ] Both views, fixed seed, and visual simplifications display correctly
- [ ] Default difficulty and visual behavior match original interactive mode
- [ ] Close/reopen repeatedly; game process exits and leaves no orphan
- [ ] Launch from paths containing spaces and non-ASCII characters
- [ ] Missing library/assets produce a readable startup error and useful log
- [ ] Additional M2: select/play/close/relaunch all 16 games through launcher
- [ ] Additional M2: invalid seed feedback, responsive launcher, parent/child shutdown

## Distribution

- [x] Audit package licenses and identify native/font/asset exceptions
- [x] Include supplemental gym3/font, native GLFW, Qt and Python notices
- [x] Exclude unused GPL-enabled FFmpeg and enforce exclusion in artifact checks
- [x] Supply Qt corresponding-source and rebuild/relink materials; modified replacement tested
- [x] Preserve complete qtbase notices/attributions with actual build configuration
- [x] Supply static libquadmath sources, build/relink helpers and replacement materials
- [x] Verify Microsoft runtime provenance and include applicable redistribution conditions
- [x] Include upstream code, font, asset and native-component notices
- [x] Verify current binary/source ZIP pairing and checksums (repeat for any changed release candidate)
- [ ] Publish matching source/binary ZIPs together, retain source access, prominently communicate Microsoft-only agreement terms
- [ ] Capture actual SmartScreen/antivirus behavior; never advise disabling protections
- [ ] Publish notes, checksums, tested platforms, requirements, known limitations
- [ ] Gate tag publication on tests **and** recorded desktop validation

Without clean-machine desktop evidence, label any shared build
**prerelease / GUI testing incomplete**. Do not infer this evidence from headless
CI or from an existing development machine with Python installed.
Do not publish a binary while the licensing/source-compliance gates remain open;
the development label does not waive dependency obligations.
