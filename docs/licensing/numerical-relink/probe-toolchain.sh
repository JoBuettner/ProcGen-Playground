#!/usr/bin/env bash
set -eu
task_root=$(cd -- "${0%/*}" && pwd)
export PATH="$task_root/toolchain/rtools40/ucrt64/bin:$task_root/toolchain/rtools40/usr/bin:$PATH"
gcc --version
gcc -v
gfortran --version
gcc -print-file-name=libquadmath.a
gcc -print-file-name=libgfortran.a
make --version
