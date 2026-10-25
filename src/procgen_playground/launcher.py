"""Lightweight desktop launcher; the original game runs in an owned child."""

from __future__ import annotations

import logging
from tkinter import Tk, StringVar, BooleanVar, ttk, messagebox
import webbrowser

from filelock import FileLock, Timeout

from .config import LaunchConfig
from .games import GAMES, GAME_BY_ID
from .logging_utils import configure_logging, log_directory
from .processes import GameSession


class Launcher:
    def __init__(self, root: Tk, initial: LaunchConfig) -> None:
        self.root = root
        self.session = GameSession()
        self.active_title = ""
        self.root.title("ProcGen Playground")
        self.root.minsize(640, 640)
        self.root.geometry("700x660")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        style = ttk.Style(root)
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))

        frame = ttk.Frame(root, padding=24)
        frame.grid(sticky="nsew")
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="ProcGen Playground", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(frame, text="16 original games. A new world each time.", style="Subtitle.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))
        ttk.Label(frame, text="Game").grid(row=2, column=0, sticky="w", padx=(0, 18))
        self.game = ttk.Combobox(frame, state="readonly", values=[game.title for game in GAMES])
        self.game.current(next(i for i, game in enumerate(GAMES) if game.id == initial.game))
        self.game.grid(row=2, column=1, sticky="ew")
        self.description = StringVar(root)
        ttk.Label(frame, textvariable=self.description, wraplength=570).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(8, 18))
        self.game.bind("<<ComboboxSelected>>", lambda _: self.update_description())

        ttk.Label(frame, text="Difficulty").grid(row=4, column=0, sticky="w")
        self.difficulty = ttk.Combobox(frame, state="readonly", values=("Easy", "Hard"), width=18)
        self.difficulty.set(initial.difficulty.title())
        self.difficulty.grid(row=4, column=1, sticky="w", pady=5)
        ttk.Label(frame, text="Level seed").grid(row=5, column=0, sticky="w")
        self.seed = StringVar(root, value="" if initial.level_seed is None else str(initial.level_seed))
        self.seed_entry = ttk.Entry(frame, textvariable=self.seed, width=22)
        self.seed_entry.grid(row=5, column=1, sticky="w", pady=5)
        ttk.Label(frame, text="Leave empty for normal procedural levels; a number repeats one level.", wraplength=570).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Label(frame, text="View").grid(row=7, column=0, sticky="w")
        self.vision = ttk.Combobox(frame, state="readonly", values=("Human", "Agent observation"), width=22)
        self.vision.set("Human" if initial.vision == "human" else "Agent observation")
        self.vision.grid(row=7, column=1, sticky="w", pady=5)
        ttk.Label(frame, text="Agent observation shows the benchmark's 64 × 64 input.").grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(0, 10))

        visuals = ttk.LabelFrame(frame, text="Visuals", padding=10)
        visuals.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.backgrounds = BooleanVar(root, value=initial.backgrounds)
        self.restrict_themes = BooleanVar(root, value=initial.restrict_themes)
        self.monochrome = BooleanVar(root, value=initial.monochrome)
        for column, (text, variable) in enumerate((
            ("Backgrounds", self.backgrounds), ("Restrict themes", self.restrict_themes),
            ("Monochrome assets", self.monochrome),
        )):
            ttk.Checkbutton(visuals, text=text, variable=variable).grid(row=0, column=column, padx=(0, 14))

        ttk.Label(frame, text="Arrow keys + Q/W/E/A/S/D: game-specific actions. O: overlay.\n"
                  "Shift+F1: save state in this session. F1: load saved state.", wraplength=570).grid(
            row=10, column=0, columnspan=2, sticky="w")
        ttk.Button(frame, text="Game descriptions & controls", command=lambda: webbrowser.open(
            "https://github.com/openai/procgen/blob/0.10.7/README.md#environments")).grid(
            row=11, column=0, columnspan=2, sticky="w", pady=(6, 12))
        self.status = StringVar(root, value="Ready. Choose a game and press Play.")
        ttk.Label(frame, textvariable=self.status, wraplength=570).grid(
            row=12, column=0, columnspan=2, sticky="w", pady=(0, 8))
        actions = ttk.Frame(frame)
        actions.grid(row=13, column=0, columnspan=2, sticky="ew")
        actions.columnconfigure(3, weight=1)
        self.play_button = ttk.Button(actions, text="Play", underline=0, command=self.play)
        self.play_button.grid(row=0, column=0, padx=(0, 8))
        self.stop_button = ttk.Button(actions, text="Stop game", underline=0, command=self.stop, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(0, 8))
        ttk.Button(actions, text="Exit", underline=1, command=self.close).grid(row=0, column=4)
        ttk.Label(frame, text="One game at a time. Closing the launcher also closes its game.").grid(
            row=14, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.root.bind("<Alt-p>", lambda _: self.play())
        self.root.bind("<Alt-s>", lambda _: self.stop())
        self.root.bind("<Alt-x>", lambda _: self.close())
        self.update_description()
        self.game.focus_set()
        self.root.after(150, self.poll_game)

    def update_description(self) -> None:
        index = self.game.current()
        if index >= 0:
            self.description.set(GAMES[index].description)

    def read_config(self) -> LaunchConfig:
        seed = self.seed.get().strip()
        try:
            level_seed = int(seed) if seed else None
        except ValueError:
            raise ValueError("Level seed must be a whole number from 0 to 2147483647, or empty.") from None
        index = self.game.current()
        if index < 0:
            raise ValueError("Please choose a game.")
        return LaunchConfig(
            game=GAMES[index].id, difficulty=self.difficulty.get().lower(),
            vision="human" if self.vision.get() == "Human" else "agent",
            level_seed=level_seed, backgrounds=self.backgrounds.get(),
            restrict_themes=self.restrict_themes.get(), monochrome=self.monochrome.get(),
        )

    def play(self) -> None:
        if self.session.process is not None:
            return
        try:
            config = self.read_config()
        except ValueError as error:
            self.status.set(str(error))
            self.seed_entry.focus_set()
            return
        try:
            self.session.start(config)
        except Exception:
            logging.exception("Could not start game process")
            messagebox.showerror("Game could not start", f"Please try again. Details: {log_directory() / 'launcher.log'}", parent=self.root)
            self.status.set("Could not start the game. You can try again.")
            return
        self.active_title = GAME_BY_ID[config.game].title
        self.play_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status.set(f"Playing {self.active_title}. Close its window to return here.")

    def poll_game(self) -> None:
        code = self.session.poll()
        if code is not None:
            self.play_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            if code == 0:
                self.status.set(f"{self.active_title} closed. Choose another game or play again.")
            else:
                self.status.set(f"{self.active_title} could not continue. You can try again.")
                messagebox.showerror("Game stopped unexpectedly",
                                     f"The game exited with code {code}.\n\nDetails: {log_directory() / 'game.log'}", parent=self.root)
        self.root.after(150, self.poll_game)

    def stop(self) -> None:
        self.session.close()
        self.play_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status.set("Game stopped. Choose a game and press Play.")

    def close(self) -> None:
        try:
            self.session.close()
        finally:
            self.root.destroy()


def run_launcher(initial: LaunchConfig) -> None:
    # One launcher per user avoids accidental duplicates and competing log
    # rotation. The OS releases this advisory lock even after a crash.
    lock = FileLock(log_directory().parent / "launcher.lock", timeout=0)
    log_directory().parent.mkdir(parents=True, exist_ok=True)
    try:
        lock.acquire()
    except Timeout:
        messagebox.showinfo("ProcGen Playground", "ProcGen Playground is already open. Please use its existing window.")
        return
    try:
        configure_logging("launcher")
        logging.info("Launcher started; initial settings: %s", initial)
        root = Tk()
        launcher = Launcher(root, initial)
        try:
            root.mainloop()
        finally:
            launcher.session.close()
    finally:
        lock.release()
        logging.info("Launcher closed")
