"""Validated options and the single mapping to the upstream environment API."""

from dataclasses import dataclass

from .games import GAME_IDS as GAME_IDS


@dataclass(frozen=True)
class LaunchConfig:
    game: str = "coinrun"
    difficulty: str = "hard"
    vision: str = "human"
    level_seed: int | None = None
    backgrounds: bool = True
    restrict_themes: bool = False
    monochrome: bool = False

    def __post_init__(self) -> None:
        if self.game not in GAME_IDS:
            raise ValueError("Choose one of the 16 standard ProcGen games.")
        if self.difficulty not in ("easy", "hard"):
            raise ValueError("Difficulty must be easy or hard.")
        if self.vision not in ("human", "agent"):
            raise ValueError("View must be human or agent.")
        if self.level_seed is not None:
            if type(self.level_seed) is not int or not 0 <= self.level_seed <= 2**31 - 1:
                raise ValueError("Level seed must be an integer from 0 to 2147483647.")
        for value in (self.backgrounds, self.restrict_themes, self.monochrome):
            if type(value) is not bool:
                raise ValueError("Visual options must be enabled or disabled.")

    def environment_options(self) -> dict[str, object]:
        options: dict[str, object] = {
            "env_name": self.game,
            "distribution_mode": self.difficulty,
            "use_backgrounds": self.backgrounds,
            "restrict_themes": self.restrict_themes,
            "use_monochrome_assets": self.monochrome,
            "paint_vel_info": False,
            "use_generated_assets": False,
            "center_agent": True,
        }
        if self.level_seed is not None:
            options.update(start_level=self.level_seed, num_levels=1)
        return options
