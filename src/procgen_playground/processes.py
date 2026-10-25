"""Testable packaged/development dispatch and ownership of one game process."""

from __future__ import annotations

import logging
import os
from pathlib import Path
import subprocess
import sys

from .config import LaunchConfig
from .windows_job import WindowsJob


def game_command(config: LaunchConfig, *, executable: str | None = None,
                 frozen: bool | None = None) -> list[str]:
    if frozen is None:
        frozen = bool(getattr(sys, "frozen", False))
    command = [executable or sys.executable]
    if not frozen:
        command += ["-m", "procgen_playground"]
    command += ["--run-game", "--game", config.game, "--difficulty", config.difficulty,
                "--vision", config.vision]
    if config.level_seed is not None:
        command += ["--level-seed", str(config.level_seed)]
    if not config.backgrounds:
        command.append("--disable-backgrounds")
    if config.restrict_themes:
        command.append("--restrict-themes")
    if config.monochrome:
        command.append("--monochrome")
    return command


class GameSession:
    """One child at a time; closing this session terminates and reaps its child."""

    def __init__(self) -> None:
        self.process: subprocess.Popen[bytes] | None = None
        self.job: WindowsJob | None = None

    def start(self, config: LaunchConfig) -> None:
        if self.process is not None:
            raise RuntimeError("Close the current game before starting another.")
        environment = os.environ.copy()
        if not getattr(sys, "frozen", False):
            source = str(Path(__file__).resolve().parents[1])
            environment["PYTHONPATH"] = os.pathsep.join(filter(None, [source, environment.get("PYTHONPATH", "")]))
        self.job = WindowsJob()
        try:
            self.process = subprocess.Popen(
                game_command(config), shell=False, env=environment, close_fds=True,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if self.process.poll() is None:
                self.job.assign(self.process.pid)
            logging.info("Started %s as child PID %s", config.game, self.process.pid)
        except Exception:
            self.close()
            raise

    def poll(self) -> int | None:
        if self.process is None:
            return None
        code = self.process.poll()
        if code is not None:
            self.process.wait()
            self.process = None
            if self.job is not None:
                self.job.close()
                self.job = None
            logging.info("Game child exited with code %s", code)
        return code

    def close(self) -> None:
        process = self.process
        try:
            if process is not None and process.poll() is None:
                process.terminate()
                process.wait(timeout=3)
        finally:
            if self.job is not None:
                self.job.close()
                self.job = None
            if process is not None:
                # Job close is a backstop if termination failed or timed out.
                process.wait(timeout=3)
            self.process = None
