"""Use upstream's interactive loop, controls, renderer, and state shortcuts."""

from pathlib import Path
from typing import Any

from .config import LaunchConfig


def check_resources() -> Path:
    # Check before importing the environment: absence must never trigger a build.
    import importlib.util

    spec = importlib.util.find_spec("procgen")
    if spec is None or spec.origin is None:
        raise RuntimeError("The bundled ProcGen package is missing. Extract the entire ZIP again.")
    root = Path(spec.origin).parent
    if not (root / "data" / "prebuilt" / "env.dll").is_file():
        raise RuntimeError("The bundled game library (env.dll) is missing. Extract the entire ZIP again.")
    if not (root / "data" / "assets" / "platformer").is_dir():
        raise RuntimeError("The bundled game assets are missing. Extract the entire ZIP again.")
    return root


def asset_root(package_root: Path) -> bytes:
    # gym3 0.3.3 encodes str options as UTF-8 but reports len(str), truncating
    # non-ASCII paths in its C interface. bytes options use the correct length.
    # Pass the exact same path as bytes; no engine or package patch is needed.
    return (str(package_root / "data" / "assets") + "/").encode("utf-8")


def make_interactive(config: LaunchConfig) -> Any:
    resources = check_resources()
    from procgen.interactive import make_interactive as upstream_make_interactive

    return upstream_make_interactive(
        vision=config.vision, record_dir=None, resource_root=asset_root(resources),
        **config.environment_options()
    )


def run_game(config: LaunchConfig) -> None:
    interactive = make_interactive(config)
    try:
        interactive.run()
    finally:
        # Upstream Interactive does not close its environment on window closure.
        from gym3 import unwrap

        unwrap(interactive._env).close()
