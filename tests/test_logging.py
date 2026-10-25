import os
from pathlib import Path
import subprocess
import sys


def test_frozen_child_output_is_logged_even_with_redirected_standard_handles(tmp_path):
    environment = os.environ.copy()
    environment["LOCALAPPDATA"] = str(tmp_path)
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    completed = subprocess.run(
        [sys.executable, "-c", "import sys; from procgen_playground.logging_utils import configure_logging; "
         "sys.frozen=True; configure_logging('game'); print('upstream output sentinel')"],
        env=environment, capture_output=True, text=True, check=True, timeout=10,
    )
    assert completed.stdout == ""
    text = (tmp_path / "ProcGenPlayground" / "logs" / "game.log").read_text(encoding="utf-8")
    assert "upstream output sentinel" in text
