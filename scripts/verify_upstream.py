"""Exercise the installed, unmodified upstream package without a game window.

This verifies native initialization/stepping, not desktop keyboard behavior.
Run from the project root with the project's Python 3.10 interpreter.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path


def probe(game: str, mode: str, vision: str, simplified: bool) -> dict:
    import numpy as np
    from procgen import ProcgenGym3Env

    options = dict(
        num=1,
        env_name=game,
        distribution_mode=mode,
        start_level=42,
        num_levels=1,
        rand_seed=123,
        use_backgrounds=not simplified,
        restrict_themes=simplified,
        use_monochrome_assets=simplified,
    )
    if vision == "human":
        options["render_mode"] = "rgb_array"
    env = ProcgenGym3Env(**options)
    try:
        digest = hashlib.sha256()
        actions = [4, 7, 7, 5, 9, 1, 10, 4] * 4
        for action in actions:
            rewards, obs, first = env.observe()
            rgb = obs["rgb"]
            assert rgb.shape == (1, 64, 64, 3) and rgb.dtype == np.uint8
            digest.update(rgb.tobytes())
            digest.update(rewards.tobytes())
            digest.update(first.tobytes())
            if vision == "human":
                human_rgb = env.get_info()[0]["rgb"]
                assert human_rgb.shape == (512, 512, 3)
                digest.update(human_rgb.tobytes())
            env.act(np.array([action], dtype=np.int32))
        saved = env.get_state()
        before = env.observe()[1]["rgb"].copy()
        env.act(np.array([7], dtype=np.int32))
        env.set_state(saved)
        np.testing.assert_array_equal(env.observe()[1]["rgb"], before)
        assert int(env.keys_to_act([["RIGHT"]])[0][0]) == 7
        return dict(game=game, mode=mode, vision=vision, simplified=simplified,
                    steps=len(actions), sha256=digest.hexdigest(), state_roundtrip=True)
    finally:
        env.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", nargs=4, metavar=("GAME", "MODE", "VIEW", "SIMPLE"))
    parser.add_argument("--output", type=Path, default=Path(".artifacts/upstream-smoke.json"))
    args = parser.parse_args()
    if args.probe:
        game, mode, view, simplified = args.probe
        print(json.dumps(probe(game, mode, view, simplified == "yes")))
        return

    from procgen.env import ENV_NAMES

    results = []
    # Separate processes avoid the engine's process-global resource state.
    for game in ENV_NAMES:
        for mode in ("easy", "hard"):
            for view, simple in (("agent", "no"), ("human", "no"), ("human", "yes")):
                command = [sys.executable, str(Path(__file__).resolve()), "--probe",
                           game, mode, view, simple]
                completed = subprocess.run(command, capture_output=True, text=True,
                                           check=True, timeout=60)
                result = json.loads(completed.stdout)
                results.append(result)
                print(f"PASS {game} {mode} {view} simplified={simple}", flush=True)
    report = dict(python=sys.version, platform=platform.platform(),
                  procgen=importlib.metadata.version("procgen"), results=results,
                  gui_verified=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(results)} native checks to {args.output}")


if __name__ == "__main__":
    main()
