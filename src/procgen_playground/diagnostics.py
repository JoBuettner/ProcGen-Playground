"""Finite native verification for a frozen binary; this is not a GUI test."""

from __future__ import annotations

import hashlib
import importlib.metadata
import platform
import sys
from typing import Any

from .config import LaunchConfig
from .game_runner import asset_root, check_resources


def verify_engine(config: LaunchConfig) -> dict[str, Any]:
    resources = check_resources()
    import numpy as np
    from procgen import ProcgenGym3Env

    options = config.environment_options()
    if config.vision == "human":
        options["render_mode"] = "rgb_array"
    env = ProcgenGym3Env(num=1, rand_seed=123, resource_root=asset_root(resources), **options)
    digest = hashlib.sha256()
    try:
        for action in [4, 7, 7, 5, 9, 1, 10, 4] * 4:
            rewards, observations, first = env.observe()
            rgb = observations["rgb"]
            assert rgb.shape == (1, 64, 64, 3) and rgb.dtype == np.uint8
            digest.update(rgb.tobytes())
            digest.update(rewards.tobytes())
            digest.update(first.tobytes())
            if config.vision == "human":
                human = env.get_info()[0]["rgb"]
                assert human.shape == (512, 512, 3)
                digest.update(human.tobytes())
            env.act(np.array([action], dtype=np.int32))
        return {
            "status": "passed", "gui_verified": False,
            "game": config.game, "difficulty": config.difficulty, "vision": config.vision,
            "level_seed": config.level_seed, "sha256": digest.hexdigest(),
            "procgen": importlib.metadata.version("procgen"),
            "python": sys.version, "platform": platform.platform(),
            "frozen": bool(getattr(sys, "frozen", False)), "resources": str(resources),
        }
    finally:
        env.close()
