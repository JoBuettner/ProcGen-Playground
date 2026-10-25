"""Dispatch the launcher, an internal game child, or finite native verification."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
from typing import NoReturn

from . import __version__
from .config import GAME_IDS, LaunchConfig
from .logging_utils import configure_logging, log_directory


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ValueError(message)


def parse_arguments(argv: list[str] | None = None) -> tuple[LaunchConfig, Path | None, bool]:
    parser = ArgumentParser(description="Play the original ProcGen environments.")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--game", choices=GAME_IDS, default="coinrun")
    parser.add_argument("--difficulty", choices=("easy", "hard"), default="hard")
    parser.add_argument("--vision", choices=("human", "agent"), default="human")
    parser.add_argument("--level-seed", type=int)
    parser.add_argument("--disable-backgrounds", action="store_true")
    parser.add_argument("--restrict-themes", action="store_true")
    parser.add_argument("--monochrome", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--run-game", action="store_true", help=argparse.SUPPRESS)
    mode.add_argument("--verify-engine", type=Path, metavar="REPORT_JSON",
                        help="write a finite native check report instead of opening a window")
    args = parser.parse_args(argv)
    config = LaunchConfig(
        game=args.game, difficulty=args.difficulty, vision=args.vision,
        level_seed=args.level_seed, backgrounds=not args.disable_backgrounds,
        restrict_themes=args.restrict_themes, monochrome=args.monochrome,
    )
    return config, args.verify_engine, args.run_game


def show_error(message: str) -> None:
    from tkinter import Tk, messagebox

    root = Tk()
    root.withdraw()
    try:
        messagebox.showerror("ProcGen Playground could not start", message, parent=root)
    finally:
        root.destroy()


def main(argv: list[str] | None = None) -> int:
    log_path: Path | None = None
    run_game_mode = False
    try:
        config, report, run_game_mode = parse_arguments(argv)
        if not run_game_mode and report is None:
            from .launcher import run_launcher

            log_path = log_directory() / "launcher.log"
            run_launcher(config)
            return 0
        log_path = configure_logging("game" if run_game_mode else "verification")
        logging.info("ProcGen Playground %s; frozen=%s; %s", __version__,
                     bool(getattr(sys, "frozen", False)), config)
        if report is not None:
            from .diagnostics import verify_engine

            result = verify_engine(config)
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        elif run_game_mode:
            from .game_runner import run_game

            run_game(config)
        logging.info("Finished successfully")
        return 0
    except Exception as error:
        logging.exception("Application failed")
        message = (f"{error}\n\nPlease extract the entire portable ZIP before launching. "
                   "The games require Windows x64, an AVX-capable CPU, and OpenGL 3.3.")
        if log_path:
            message += f"\n\nDetails: {log_path}"
        # The launcher observes a child's exit and shows its error, avoiding
        # duplicate dialogs or a child waiting forever on an unseen modal.
        if not run_game_mode:
            try:
                show_error(message)
            except Exception:
                logging.exception("Could not display the error dialog")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
