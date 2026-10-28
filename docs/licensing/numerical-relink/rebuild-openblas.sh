#!/usr/bin/env bash
# Rebuild only in this disposable numerical workspace. No runtime DLL is replaced.
set -eu
task_root=$(cd -- "${0%/*}" && pwd)
export PATH="$task_root/toolchain/rtools40/ucrt64/bin:$task_root/toolchain/rtools40/usr/bin:$PATH"
export MSYSTEM=UCRT64
export LIBNAMESUFFIX=v0.3.23-293-gc2f4bdbb-gcc_10_3_0
cd "$task_root/build/openblas"
gcc --version
gfortran --version
make -j4 BINARY=64 DYNAMIC_ARCH=1 USE_THREAD=1 USE_OPENMP=0 \
    NUM_THREADS=24 NO_WARMUP=1 NO_AFFINITY=1 CONSISTENT_FPCSR=1 \
    BUILD_LAPACK_DEPRECATED=1 TARGET=PRESCOTT BUFFERSIZE=20 \
    LDFLAGS="-lucrt -static -static-libgcc" \
    COMMON_OPT="-O2 -march=x86-64 -mtune=generic -fno-asynchronous-unwind-tables" \
    FCOMMON_OPT="-O2 -march=x86-64 -mtune=generic -fno-asynchronous-unwind-tables -frecursive -ffpe-summary=invalid,zero -fdefault-integer-8" \
    MAX_STACK_ALLOC=2048 INTERFACE64=1 SYMBOLSUFFIX=64_
