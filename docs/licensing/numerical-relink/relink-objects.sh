#!/usr/bin/env bash
# Fast LGPL relink route using supplied OpenBLAS application objects.
# No full OpenBLAS compilation or repository checkout is needed by this step.
set -eu
task_root=$(cd -- "${0%/*}" && pwd)
export PATH="$task_root/toolchain/rtools40/ucrt64/bin:$task_root/toolchain/rtools40/usr/bin:$PATH"
export MSYSTEM=UCRT64
inputs=$(cd -- "${NUMERICAL_RELINK_INPUTS:-$task_root/relink-inputs}" && pwd)
cd "$inputs"
sha256sum -c SHA256SUMS
test -f "$task_root/build/quadmath/.libs/libquadmath.a"
output="$task_root/build/object-relink"
mkdir -p "$output"
cp "$inputs/OpenBLAS-exports.def" "$output/OpenBLAS-exports.def"
if [ "${1:-}" = '--probe' ]; then
    printf '\nprocgen_quadmath_relink_probe\n' >> "$output/OpenBLAS-exports.def"
elif [ "$#" -ne 0 ]; then
    echo 'Usage: relink-objects.sh [--probe]' >&2
    exit 2
fi
gcc -m64 -L"$task_root/build/quadmath/.libs" -lucrt -static -static-libgcc \
    "$output/OpenBLAS-exports.def" "$inputs/dllinit.obj" \
    -shared -o "$output/procgen-openblas-object-relink.dll" \
    -Wl,--out-implib,"$output/procgen-openblas-object-relink.dll.a" \
    -Wl,-Map,"$output/procgen-openblas-object-relink.map" \
    -Wl,--whole-archive "$inputs/OpenBLAS-application-objects.a" -Wl,--no-whole-archive \
    -lgfortran -lmoldname -lmingwex -lmsvcrt -lquadmath -lm \
    -lmoldname -lmingwex -lmsvcrt -lpthread -lmoldname -lmingwex -lmsvcrt -lgfortran
tr '\\' '/' < "$output/procgen-openblas-object-relink.map" | grep -Fq 'build/quadmath/.libs/libquadmath.a'
if [ "${1:-}" = '--probe' ]; then
    grep -Fq 'procgen_quadmath_relink_probe' "$output/procgen-openblas-object-relink.map"
fi
