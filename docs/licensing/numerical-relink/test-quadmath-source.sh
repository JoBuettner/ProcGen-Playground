#!/usr/bin/env bash
set -eu
task_root=$(cd -- "${0%/*}" && pwd)
export PATH="$task_root/toolchain/rtools40/ucrt64/bin:$task_root/toolchain/rtools40/usr/bin:$PATH"
gcc -O2 -m64 -I"$task_root/gcc-source/gcc-10.3.0/libquadmath" \
    "$task_root/quadmath-probe.c" "$task_root/build/quadmath/.libs/libquadmath.a" \
    -static -static-libgcc -lucrt -lm -o "$task_root/build/quadmath-probe.exe"
"$task_root/build/quadmath-probe.exe"
