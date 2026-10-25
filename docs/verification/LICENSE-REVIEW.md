# License audit implementation review — 2026-10-25

Baseline: `4e660c6`; reviewed the ensuing working changes and new audit/notices.
User scope: portable ZIP only, recommend a license and audit dependencies,
identify actual UI checks; full desktop/separate-PC acceptance stays at the end.

## Standards axis

Independent review found no actionable standards violations or substantial
Fowler smell findings in the packaging, notice collection or verification changes.

## Spec/correctness axis

One finding was raised and resolved: libquadmath in NumPy's OpenBLAS DLL has
LGPL-2.1-or-later terms separately from libgfortran's GCC runtime exception.
Added its full license and an explicit source/relinking review gate, propagated
to attribution/status/releasing docs and required-notice checks. The reviewer
confirmed resolution and reported no remaining findings.

Totals after correction: **0 unresolved standards findings; 0 unresolved spec findings**.
This code/documentation review does not establish legal redistribution clearance.

## Validation and residual provenance

- 85 tests and strict mypy on 10 source modules passed.
- Rebuilt the windowed portable artifact; final frozen parity: 96/96 passed,
  1,290 upstream data files unchanged, required supplemental notices included,
  no FFmpeg executable. See `frozen-license-2026-10-25.json`.
- `bundled-license-audit-2026-10-25.json` records 99 native files with SHA-256,
  selected import tables, and build-input source categories.
- That manifest also identifies 45 Microsoft runtime/API-set files selected
  through the builder's ambient Codex cached libheif runtime directory. These
  are Microsoft runtime files, not libheif code. Before publication, use a
  controlled redistributable source and verify its applicable terms/rights.
- Qt source/relinking materials, Qt subcomponent inventory, libquadmath LGPL
  compliance and Microsoft provenance remain release gates. MIT on our code
  and the collected notices alone do not clear them.
- No additional desktop or separate-PC acceptance pass is claimed here.
