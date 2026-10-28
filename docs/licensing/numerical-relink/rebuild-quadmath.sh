#!/usr/bin/env bash
# Rebuild the LGPL library from the preserved GCC source, in a disposable tree.
set -eu
task_root=$(cd -- "${0%/*}" && pwd)
export PATH="$task_root/toolchain/rtools40/ucrt64/bin:$task_root/toolchain/rtools40/usr/bin:$PATH"
export MSYSTEM=UCRT64
mkdir -p "$task_root/build/quadmath"
cd "$task_root/build/quadmath"
bash "$task_root/gcc-source/gcc-10.3.0/libquadmath/configure" \
    --build=x86_64-pc-msys --host=x86_64-w64-mingw32 \
    --target=x86_64-w64-mingw32 --disable-multilib \
    --enable-static --disable-shared \
    --prefix="$task_root/build/quadmath-install" \
    CC=gcc CFLAGS="-O2 -march=x86-64 -mtune=generic -fno-asynchronous-unwind-tables"
make -j4
