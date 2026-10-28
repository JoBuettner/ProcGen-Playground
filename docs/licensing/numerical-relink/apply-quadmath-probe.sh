#!/usr/bin/env bash
set -eu
task_root=$(cd -- "${0%/*}" && pwd)
export PATH="$task_root/toolchain/rtools40/ucrt64/bin:$task_root/toolchain/rtools40/usr/bin:$PATH"
cd "$task_root/gcc-source/gcc-10.3.0"
if grep -q procgen_quadmath_relink_probe libquadmath/printf/quadmath-printf.c; then
    echo 'Marked probe modification already present.'
else
    patch --batch -p1 -i "$task_root/quadmath-relink-probe.patch"
fi
