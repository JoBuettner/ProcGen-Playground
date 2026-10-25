# Final desktop acceptance

Record artifact version/SHA-256, Windows version, CPU/GPU, and tester/date.
Keep the existing development-PC results separate from the final separate-PC
test without Python. Both are useful evidence; one does not stand in for the other.
By user decision, run the complete desktop walkthrough and separate-PC test at
the end of development. The table below is a fresh final-artifact matrix; empty
cells do not erase earlier representative checks.

## What remains unverified in the UI

No known required UI feature is missing from implementation. Outstanding checks:

- Duplicate-instance message after starting a second launcher process.
- Child startup failure (missing engine/assets), readable dialog/log path,
  dismissal and retry; launcher process-start failure dialog where practical.
- Full Tab traversal/focus and keyboard operation of each field/button.
- Controls link opening the intended upstream page in the default browser.
- Easy selection, backgrounds off, theme restriction and their visible effects.
- Seed boundary UI feedback (`-1`, `2147483648`) and accepted boundaries
  (`0`, `2147483647`); blank/42 normal launches are already demonstrated.
- Complete 16-game keyboard-action/close/relaunch matrix below, repeated on the
  final artifact, plus separate-PC portability.

Already demonstrated on this PC: CoinRun controls, CoinRun/Heist/Cave Flyer
rendering, close/return to menu, seed 42, agent view, monochrome, noninteger-seed
feedback, Stop, parent-close child cleanup, Alt+P/S/X, no console, Unicode path
startup, and game log capture. Automated tests cover option mapping, seed bounds
and process lifecycle; those do not claim physical desktop coverage.

## Final artifact walkthrough

For each game below: select in the menu, Play, check rendering and keyboard
actions, close its window, then Play it again and close it. Verify the menu
remains responsive and lets you switch games. Completing or winning a level
is not required for this startup/lifecycle check.

| Game | Starts and renders | Keyboard actions | Close/relaunch |
| --- | --- | --- | --- |
| Big Fish | [ ] | [ ] | [ ] |
| Boss Fight | [ ] | [ ] | [ ] |
| Cave Flyer | [ ] | [ ] | [ ] |
| Chaser | [ ] | [ ] | [ ] |
| Climber | [ ] | [ ] | [ ] |
| CoinRun | [ ] | [ ] | [ ] |
| Dodgeball | [ ] | [ ] | [ ] |
| FruitBot | [ ] | [ ] | [ ] |
| Heist | [ ] | [ ] | [ ] |
| Jumper | [ ] | [ ] | [ ] |
| Leaper | [ ] | [ ] | [ ] |
| Maze | [ ] | [ ] | [ ] |
| Miner | [ ] | [ ] | [ ] |
| Ninja | [ ] | [ ] | [ ] |
| Plunder | [ ] | [ ] | [ ] |
| StarPilot | [ ] | [ ] | [ ] |

Other scenarios:

- [ ] Play with empty seed, seed `0`, and seed `42`.
- [ ] Noninteger, negative, and oversized seeds give readable feedback.
- [ ] Easy/Hard, Human/Agent observation, and each visual checkbox work.
- [ ] Stop game ends the child and allows another Play.
- [ ] Closing the launcher while playing ends both windows/processes.
- [ ] Opening the launcher twice gives clear existing-instance feedback.
- [ ] Tab and the Alt+P / Alt+S / Alt+X accelerators work.
- [ ] Game descriptions & controls opens the intended page in the default browser.
- [ ] Extract and run from a path containing spaces and non-ASCII characters.
- [ ] No console, runtime download, Python installation, or compilation is needed.
- [ ] Test launcher/game log paths and startup error behavior in a disposable copy.

Keep all extracted files together. For the final portable test, use the actual
release ZIP rather than copying only the EXE out of its folder.
