# Release validation checklist

Current output is an M1 development artifact, not a public release. M2 launcher,
M4 installer, and tag publication are deferred until their preceding gates pass.

## Automated evidence

- [ ] Fresh Windows x64/Python 3.10 setup using hashed lock files
- [ ] `scripts/build_windows.ps1` completes successfully
- [ ] Every environment initializes, observes, steps, restores state, and closes
- [ ] Frozen outputs match unmodified upstream for all 96 native cases
- [ ] Extracted data/native files match original package hashes
- [ ] Space/non-ASCII extraction path and stripped environment tests pass
- [ ] ZIP checksum, version, size, build log, dependency inventory archived
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

- [ ] Finish native Qt/C++ dependency license/source-compliance review
- [ ] Include upstream code and asset attributions and all relevant notices
- [ ] Test optional installer, shortcuts, uninstall, and user-data preservation
- [ ] Capture actual SmartScreen/antivirus behavior; never advise disabling protections
- [ ] Publish notes, checksums, tested platforms, requirements, known limitations
- [ ] Gate tag publication on tests **and** recorded desktop validation

Without clean-machine desktop evidence, label any shared build
**prerelease / GUI testing incomplete**. Do not infer this evidence from headless
CI or from an existing development machine with Python installed.
