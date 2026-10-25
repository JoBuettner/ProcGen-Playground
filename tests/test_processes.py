import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import Mock

import pytest

from procgen_playground.__main__ import parse_arguments
from procgen_playground.config import LaunchConfig
from procgen_playground.games import GAMES, GAME_IDS
from procgen_playground.processes import GameSession, game_command
from procgen_playground.windows_job import WindowsJob


@pytest.mark.parametrize("game", GAME_IDS)
@pytest.mark.parametrize("frozen", [True, False])
def test_child_arguments_roundtrip_all_settings_without_external_python(game, frozen):
    config = LaunchConfig(game=game, difficulty="easy", vision="agent", level_seed=0,
                          backgrounds=False, restrict_themes=True, monochrome=True)
    executable = "C:/Games/Prüfung/ProcGenPlayground.exe" if frozen else "C:/Dev env/python.exe"
    command = game_command(config, executable=executable, frozen=frozen)
    assert command[0] == executable
    if frozen:
        assert "-m" not in command and "python" not in " ".join(command).lower()
        args = command[1:]
    else:
        assert command[1:3] == ["-m", "procgen_playground"]
        args = command[3:]
    parsed, report, run_game = parse_arguments(args)
    assert parsed == config
    assert report is None and run_game is True


def test_no_seed_flag_preserves_unlimited_upstream_levels():
    assert "--level-seed" not in game_command(LaunchConfig())


def test_internal_modes_cannot_be_combined():
    with pytest.raises(ValueError):
        parse_arguments(["--run-game", "--verify-engine", "report.json"])


def test_catalog_has_unique_titles_and_descriptions():
    assert len({game.title for game in GAMES}) == len(GAME_IDS) == 16
    assert all(game.description for game in GAMES)


@pytest.mark.skipif(os.name != "nt", reason="Windows process ownership")
def test_job_close_terminates_its_child():
    job = WindowsJob()
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                             creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        job.assign(child.pid)
        job.close()
        # Kill-on-close may use exit code zero; completing within three seconds
        # rather than the child's 60-second sleep establishes termination.
        child.wait(timeout=3)
        assert child.poll() is not None
    finally:
        job.close()
        if child.poll() is None:
            child.kill()
        child.wait()


@pytest.mark.skipif(os.name != "nt", reason="Windows process ownership")
def test_abrupt_owner_exit_kills_assigned_game(tmp_path):
    import ctypes
    from ctypes import wintypes

    pid_file = tmp_path / "child.pid"
    source = (
        "import subprocess,sys,time; from pathlib import Path; "
        "from procgen_playground.windows_job import WindowsJob; "
        "job=WindowsJob(); "
        "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
        "job.assign(child.pid); Path(sys.argv[1]).write_text(str(child.pid)); time.sleep(60)"
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    owner = subprocess.Popen([sys.executable, "-c", source, str(pid_file)], env=environment,
                             creationflags=subprocess.CREATE_NO_WINDOW)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    child_handle = None
    try:
        deadline = time.monotonic() + 5
        while not pid_file.exists() and time.monotonic() < deadline and owner.poll() is None:
            time.sleep(0.01)
        assert pid_file.exists(), "Owner did not create and assign a child"
        child_handle = kernel.OpenProcess(0x00100000, False, int(pid_file.read_text()))
        assert child_handle
        owner.kill()
        owner.wait(timeout=3)
        assert kernel.WaitForSingleObject(child_handle, 3000) == 0
    finally:
        if owner.poll() is None:
            owner.kill()
        owner.wait()
        if child_handle:
            kernel.CloseHandle(child_handle)


@pytest.mark.skipif(os.name != "nt", reason="Windows process ownership")
def test_session_rejects_duplicate_and_reaps_child_on_close(monkeypatch):
    monkeypatch.setattr("procgen_playground.processes.game_command",
                        lambda _: [sys.executable, "-c", "import time; time.sleep(60)"])
    session = GameSession()
    try:
        session.start(LaunchConfig())
        child = session.process
        assert child is not None and child.poll() is None
        with pytest.raises(RuntimeError, match="current game"):
            session.start(LaunchConfig(game="heist"))
        session.close()
        assert child.poll() is not None and session.process is None
        session.close()  # Repeated close is safe.
    finally:
        session.close()


def test_start_failure_does_not_keep_a_job_or_process(monkeypatch):
    job = Mock()
    monkeypatch.setattr("procgen_playground.processes.WindowsJob", lambda: job)
    monkeypatch.setattr("procgen_playground.processes.subprocess.Popen", Mock(side_effect=OSError("cannot start")))
    session = GameSession()
    with pytest.raises(OSError, match="cannot start"):
        session.start(LaunchConfig())
    assert session.process is None and session.job is None
    job.close.assert_called_once()


def test_finished_child_is_reported_once_and_can_be_relaunched(monkeypatch):
    job = Mock()
    monkeypatch.setattr("procgen_playground.processes.WindowsJob", lambda: job)
    process = Mock()
    process.poll.side_effect = [None, 7]
    monkeypatch.setattr("procgen_playground.processes.subprocess.Popen", Mock(return_value=process))
    session = GameSession()
    session.start(LaunchConfig())
    assert session.poll() == 7
    assert session.poll() is None and session.process is None
    job.close.assert_called_once()
    process.wait.assert_called_once()


def test_dispatch_defaults_to_launcher_but_child_runs_game(monkeypatch):
    from procgen_playground import __main__ as entry

    launcher = Mock()
    runner = Mock()
    monkeypatch.setattr("procgen_playground.launcher.run_launcher", launcher)
    monkeypatch.setattr("procgen_playground.game_runner.run_game", runner)
    monkeypatch.setattr(entry, "configure_logging", lambda _: Path("test.log"))
    assert entry.main([]) == 0
    launcher.assert_called_once_with(LaunchConfig())
    runner.assert_not_called()
    assert entry.main(["--run-game", "--game", "heist"]) == 0
    runner.assert_called_once_with(LaunchConfig(game="heist"))


def test_child_failure_returns_to_parent_without_modal(monkeypatch):
    from procgen_playground import __main__ as entry

    monkeypatch.setattr(entry, "configure_logging", lambda _: Path("test.log"))
    monkeypatch.setattr("procgen_playground.game_runner.run_game", Mock(side_effect=RuntimeError("missing DLL")))
    dialog = Mock()
    monkeypatch.setattr(entry, "show_error", dialog)
    assert entry.main(["--run-game"]) == 1
    dialog.assert_not_called()
