# License preparation verification — 2026-10-28

The launcher remains MIT licensed. Current distribution materials are described
in `../licensing/REDISTRIBUTION.md`; the 2026-10-25 audit is historical.

- 103 unit tests and strict mypy for 10 source modules passed.
- Qt 5.13.2 was rebuilt with the recorded upstream configuration. A modified
  Qt version function was relinked into ProcGen and loaded in a disposable app
  copy: nine native cases matched upstream. See `qt-relink-2026-10-28.json`.
- Ordinary OpenBLAS reconstruction, modified-libquadmath relinking, and the
  supplied application-object shortcut each preserved all 9,360 original
  exports and passed 12 numerical comparisons with zero differences. Modified
  builds expose the added source query. Evidence and complete instructions are
  under `../licensing/numerical-relink/`; original runtime files were unchanged.
- Signed Microsoft VC14 14.51.36247.0 files are extracted from a pinned official
  package as data. No runtime installer or MSI was executed. The installed
  Community 2022 redistribution route, original terms and file provenance are
  retained under `third_party/microsoft/` in the source project.
- Standards review found an overly broad wheel-provenance check. It now
  requires locked distribution ownership and validates wheel RECORD hashes.
  Spec review found the original CRT 14.29 selection was too old for bundled
  extensions linked with 14.51. The selected CRT and version-floor enforcement
  correct that finding; a negative regression test covers a newer dependency.
  Follow-up standards and spec reviews found no remaining actionable findings.

The final build log is `.artifacts/licensing-build-2026-10-28.log`. Current
binary/source pairing, every source-file hash, all native input provenance,
notice coverage, runtime exports and observable linker-version checks are
recorded by `.artifacts/license-bundle-verification.json`. The source checksum
is kept in its ZIP sidecar rather than embedded here, avoiding a self-reference
when this record is included in the source companion.

Full desktop acceptance and testing on another PC without Python remain
deferred by agreement. No GitHub CI run, public release, or download-page
compliance is claimed. Publish matching binary/source ZIPs together and preserve
the component conditions specified in the redistribution record.
