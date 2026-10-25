# Final desktop acceptance

Record artifact version/SHA-256, Windows version, CPU/GPU, and tester/date.
Keep the existing development-PC results separate from the final separate-PC
test without Python. Both are useful evidence; one does not stand in for the other.

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
- [ ] Extract and run from a path containing spaces and non-ASCII characters.
- [ ] No console, runtime download, Python installation, or compilation is needed.
- [ ] Test launcher/game log paths and startup error behavior in a disposable copy.

Keep all extracted files together. For the final portable test, use the actual
release ZIP rather than copying only the EXE out of its folder.
