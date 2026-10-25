# Third-party provenance and redistribution status

ProcGen Playground is an independent wrapper, not an official OpenAI product.
Wrapper source is under the root MIT license.

## ProcGen

- Package: OpenAI ProcGen 0.10.7, CPython 3.10 `win_amd64` wheel from PyPI.
- Engine and Python package are unmodified; the wrapper calls
  `procgen.interactive.make_interactive` directly.
- Code: MIT; included at `third_party/procgen/LICENSE`.
- Assets: multiple licenses; the upstream asset notices must be included in
  `third_party/procgen/ASSET_LICENSES.md`.
- Source: https://github.com/openai/procgen
- Source tag: `0.10.7`, commit `5e1dbf341d291eff40d1f9e0c0a0d5003643aebf`.
- Assets are redistributed unchanged; their individual authors and license
  links appear in the bundled original `ASSET_LICENSES.md`.

## Bundled dependencies

The build collects installed distribution license files and CPython's license
into `third_party/`. The pinned dependency inventory is in
`requirements-windows.txt`. gym3, GLFW, ModernGL, NumPy, Pillow, CFFI, and the
other libraries retain their respective licenses. PyInstaller's bootloader
exception applies to the frozen application's distribution.

The bundled notice inventory includes build-tool notices as well as runtime
notices; inclusion there does not mean every listed package is shipped as code.
Tcl/Tk notices are from the upstream `core-8-6-12` tags:
https://github.com/tcltk/tcl/blob/core-8-6-12/license.terms and
https://github.com/tcltk/tk/blob/core-8-6-12/license.terms.

**Redistribution audit pending:** the native ProcGen wheel's statically linked
Qt and other C++ components require a source/notices/compliance review before
public release. A successful executable build does not clear this release gate.
No public release has been published.
