# Rebuild and modify the numerical library

These helpers reproduce the numerical source/relink experiment recorded in
`../NUMERICAL-SOURCES.md`. They produce disposable outputs. The application,
installed wheel and packaged original DLL are not changed. Reproduction is an
ABI and functionality check, not a claim of a byte-for-byte historical rebuild.

Use a Windows x64 host with PowerShell, Windows `tar`, and enough space for the
extracted source, tools and object files. The exact portable Rtools prerequisite
is `rtools40-x86_64.7z` from the
[official 2022-02-06 release](https://github.com/r-windows/rtools-installer/releases/tag/2022-02-06).
Obtain it separately; it is not redistributed in the source companion. Its
expected SHA-256 is
`a44c6bf6099c5ed18e2feba5dd1fdc4a62a5fd1dc06683e39ca0f0d720af9a6a`.
The helper performs the hash verification. No system install is needed.

From the extracted source companion's root, prepare the workspace:

```powershell
& .\project\docs\licensing\numerical-relink\prepare-sources.ps1 `
    -ArchiveDirectory .\archives -Workspace .\numerical-work `
    -ToolchainArchive C:\Downloads\rtools40-x86_64.7z
Set-Location .\numerical-work
$env:MSYSTEM = 'UCRT64'
$bash = '.\toolchain\rtools40\usr\bin\bash.exe'
& $bash --noprofile --norc ./probe-toolchain.sh *> toolchain-probe.log
& $bash --noprofile --norc ./rebuild-openblas.sh *> rebuild-openblas.log
```

Check each command's `$LASTEXITCODE` is zero before continuing. The full
`DYNAMIC_ARCH` build includes the historical CPU variants and LAPACK and can
take substantial time. Configuration and linker flags are fixed in the script
and match the preserved historical Windows recipe. The GCC and MinGW archives,
their Rtools patch recipes and the historical builder archive remain intact
under `archives/`; extraction does not replace those full sources.

Build the independent LGPL library, apply the documented harmless source
change, and relink the OpenBLAS DLL:

```powershell
& $bash --noprofile --norc ./rebuild-quadmath.sh *> rebuild-quadmath.log
& $bash --noprofile --norc ./apply-quadmath-probe.sh
& $bash --noprofile --norc ./rebuild-quadmath.sh *> rebuild-quadmath-modified.log
& $bash --noprofile --norc ./test-quadmath-source.sh *> quadmath-source-test.log
& $bash --noprofile --norc ./relink-openblas.sh *> relink-openblas.log
```

The probe patch changes a copied libquadmath source file, with a dated notice,
by adding a query function. The original numerical functions are unchanged.
The source test calls the query and computes/formats `sqrtq(2)` using that
source-built static library. The relink uses the full rebuilt OpenBLAS archive
and the replacement `build/quadmath/.libs/libquadmath.a`; the generated link map
is checked for that path and the new symbol. The modified output is
`build/openblas/procgen-openblas-modified-quadmath.dll`.

For a different libquadmath change, edit the copied LGPL source in
`gcc-source/gcc-10.3.0/libquadmath/`, rebuild it, and rerun the relink script.
Keep its public ABI intact and preserve a dated modification notice. The
full source, generated object archive, `.def`, configuration and link rule
allow this without changing the original game. The probe-specific source test
and query assertion are demonstration checks; change them to match a different
modification.

Optional NumPy ABI/numerical verification uses Python 3.10 with the unmodified
NumPy 1.26.4 Windows x64 wheel and `pefile`, as installed in the development
environment. Pass the actual absolute `site-packages` path to it:

```powershell
$python = 'D:\path\to\development\.venv\Scripts\python.exe'
$site = 'D:\path\to\development\.venv\Lib\site-packages'
$ordinary = Get-ChildItem .\build\openblas\libopenblas*.dll | Select-Object -First 1
& $python ./verify-relinked-numpy.py --installed-site $site `
    --dll $ordinary.FullName --report ordinary-rebuild-verification.json
& $python ./verify-relinked-numpy.py --installed-site $site `
    --dll ./build/openblas/procgen-openblas-modified-quadmath.dll `
    --probe-required --report relink-verification.json
```

The verifier compares all original DLL exports, copies NumPy and its library
directory to `replacement-site/`, replaces only that copied DLL, and uses fresh
Python processes for both libraries. It exercises float32/float64/complex64/
complex128 matrix multiplication, solve and SVD, compares the outputs and
residuals, calls the modified library's query, and confirms the installed
original DLL's hash is unchanged. JSON records contain the actual loaded paths,
configuration, hashes, numerical differences and export results. These checks
do not replace the application's desktop or separate-PC acceptance tests.

## Faster route using supplied application objects

The companion's `generated/numerical/` directory supplies the full OpenBLAS/
LAPACK application object archive, its export definition and `dllinit.obj`.
`../NUMERICAL-RELINK-INPUTS.json` records each input's hash, size, source and
license. These are application objects, not redistributed compiler binaries.
The complete upstream sources remain in `archives/`.

Prepare a workspace with `prepare-sources.ps1` as above, then copy the contents
of `generated/numerical/` into the workspace's `relink-inputs/` directory. Run
only the following build steps from that workspace to demonstrate a libquadmath
change without repeating the full OpenBLAS compilation:

```powershell
$env:MSYSTEM = 'UCRT64'
$bash = '.\toolchain\rtools40\usr\bin\bash.exe'
& $bash --noprofile --norc ./apply-quadmath-probe.sh
& $bash --noprofile --norc ./rebuild-quadmath.sh *> rebuild-quadmath-modified.log
& $bash --noprofile --norc ./test-quadmath-source.sh *> quadmath-source-test.log
& $bash --noprofile --norc ./relink-objects.sh --probe *> relink-objects.log
```

`relink-objects.sh` first verifies `SHA256SUMS`. It links directly with the
supplied archive, export definition and startup object, plus the replacement
libquadmath and the separately obtained matching compiler's runtime libraries.
The generated Makefile/configuration files are provenance records with the
original local paths; this shortcut does not use those paths. The output is
`build/object-relink/procgen-openblas-object-relink.dll`.

Use the same NumPy verifier with that DLL and `--probe-required`. For another
libquadmath modification that does not add the demonstration query, omit
`--probe` from the relink command and `--probe-required` from verification.
The resulting library can replace the original named DLL in a disposable copy
of the application or wheel. Keep the production original intact until the
modified build has been tested for the intended use.
