import pytest

from procgen_playground.config import GAME_IDS, LaunchConfig
from procgen_playground.__main__ import parse_arguments


def test_defaults_match_original_interactive_mode():
    config, report, run_game = parse_arguments([])
    assert config == LaunchConfig(game="coinrun", difficulty="hard", vision="human")
    assert report is None
    assert run_game is False
    assert config.environment_options() == {
        "env_name": "coinrun", "distribution_mode": "hard",
        "use_backgrounds": True, "restrict_themes": False,
        "use_monochrome_assets": False, "paint_vel_info": False,
        "use_generated_assets": False, "center_agent": True,
    }


@pytest.mark.parametrize("game", GAME_IDS)
def test_all_standard_games_are_accepted(game):
    config, _, _ = parse_arguments(["--game", game])
    assert config.environment_options()["env_name"] == game


def test_exactly_standard_catalog():
    from procgen.env import ENV_NAMES

    assert list(GAME_IDS) == ENV_NAMES
    assert len(set(GAME_IDS)) == 16
    assert "coinrun_old" not in GAME_IDS


@pytest.mark.parametrize("seed", [0, 42, 2147483647])
def test_seed_selects_one_level(seed):
    options = LaunchConfig(level_seed=seed).environment_options()
    assert options["start_level"] == seed
    assert options["num_levels"] == 1


@pytest.mark.parametrize("kwargs", [
    {"game": "coinrun_old"}, {"game": "../../x"}, {"difficulty": "extreme"},
    {"vision": "other"}, {"level_seed": -1}, {"level_seed": 2147483648},
    {"level_seed": True}, {"level_seed": "42"}, {"level_seed": 1.5},
    {"backgrounds": "false"}, {"restrict_themes": 1}, {"monochrome": None},
])
def test_invalid_configuration_rejected_before_native_start(kwargs):
    with pytest.raises(ValueError):
        LaunchConfig(**kwargs)


def test_cli_visual_options_map_to_upstream():
    config, _, _ = parse_arguments([
        "--game", "heist", "--difficulty", "easy", "--vision", "agent",
        "--level-seed", "0", "--disable-backgrounds", "--restrict-themes", "--monochrome",
    ])
    assert config.vision == "agent"
    options = config.environment_options()
    assert options["env_name"] == "heist" and options["distribution_mode"] == "easy"
    assert options["start_level"] == 0 and options["num_levels"] == 1
    assert options["use_backgrounds"] is False
    assert options["restrict_themes"] is True
    assert options["use_monochrome_assets"] is True


@pytest.mark.parametrize("args", [["--game", "bad"], ["--level-seed", "abc"], ["--unknown"]])
def test_invalid_cli_raises_readable_error(args):
    with pytest.raises(ValueError):
        parse_arguments(args)
