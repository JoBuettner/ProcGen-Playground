"""Use the pinned VC14 GLFW build before gym3 imports its Python bindings."""

import os
from pathlib import Path
import sys

# The binding's fallback bundled with glfw 1.12 preloads VC11. Its documented
# library override loads the same-version VC14 build directly instead.
os.environ["PYGLFW_LIBRARY"] = str(Path(sys._MEIPASS) / "glfw" / "glfw3.dll")
