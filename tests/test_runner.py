from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from procgen_playground.config import LaunchConfig
from procgen_playground import game_runner


def test_interactive_delegates_to_unmodified_upstream(monkeypatch):
    import procgen.interactive

    factory = Mock(return_value=object())
    monkeypatch.setattr(procgen.interactive, "make_interactive", factory)
    config = LaunchConfig(game="caveflyer", vision="agent", level_seed=42)
    assert game_runner.make_interactive(config) is factory.return_value
    factory.assert_called_once_with(vision="agent", record_dir=None,
                                    resource_root=game_runner.asset_root(game_runner.check_resources()),
                                    **config.environment_options())


def test_non_ascii_resource_root_uses_bytes_for_correct_c_length():
    root = Path("C:/Spiele/Prüfung/游戏/procgen")
    encoded = game_runner.asset_root(root)
    assert type(encoded) is bytes
    assert encoded.decode("utf-8") == str(root / "data" / "assets") + "/"
    assert len(encoded) > len(encoded.decode("utf-8"))


def test_resources_missing_fails_before_importing_engine(monkeypatch, tmp_path):
    import importlib.util

    monkeypatch.setattr(importlib.util, "find_spec", lambda _: SimpleNamespace(origin=str(tmp_path / "__init__.py")))
    with pytest.raises(RuntimeError, match="env.dll"):
        game_runner.check_resources()


def test_environment_closed_even_when_interactive_loop_fails(monkeypatch):
    import gym3

    env = Mock()
    interactive = SimpleNamespace(_env=env, run=Mock(side_effect=RuntimeError("renderer failed")))
    monkeypatch.setattr(game_runner, "make_interactive", lambda _: interactive)
    monkeypatch.setattr(gym3, "unwrap", lambda value: value)
    with pytest.raises(RuntimeError, match="renderer failed"):
        game_runner.run_game(LaunchConfig())
    env.close.assert_called_once()


def test_log_path_uses_user_data_not_installation(monkeypatch, tmp_path):
    from procgen_playground.logging_utils import log_directory

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert log_directory() == tmp_path / "ProcGenPlayground" / "logs"
