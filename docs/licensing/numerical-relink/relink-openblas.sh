#!/usr/bin/env bash
# Relink a disposable OpenBLAS DLL against the source-built libquadmath.
# Original installed and packaged files are never targeted by this script.
set -eu
task_root=$(cd -- "${0%/*}" && pwd)
export PATH="$task_root/toolchain/rtools40/ucrt64/bin:$task_root/toolchain/rtools40/usr/bin:$PATH"
export MSYSTEM=UCRT64
export LIBNAMESUFFIX=v0.3.23-293-gc2f4bdbb-gcc_10_3_0
cd "$task_root/build/openblas/exports"
test -f "$task_root/build/quadmath/.libs/libquadmath.a"
cat > procgen-relink.mk <<'EOF'
include Makefile

procgen-relink: ../$(LIBNAME) $(LIBPREFIX).def dllinit.$(SUFFIX)
	cp $(LIBPREFIX).def procgen-relink.def
	printf '\nprocgen_quadmath_relink_probe\n' >> procgen-relink.def
	$(CC) $(CFLAGS) -L$(QUADMATH_REPLACEMENT) $(LDFLAGS) procgen-relink.def dllinit.$(SUFFIX) \
	-shared -o ../procgen-openblas-modified-quadmath.dll -Wl,--out-implib,../procgen-openblas-modified-quadmath.dll.a \
	-Wl,-Map,../procgen-openblas-modified-quadmath.map \
	-Wl,--whole-archive ../$(LIBNAME) -Wl,--no-whole-archive $(FEXTRALIB) $(EXTRALIB)
EOF
make -f procgen-relink.mk procgen-relink \
    QUADMATH_REPLACEMENT="$task_root/build/quadmath/.libs" \
    BINARY=64 DYNAMIC_ARCH=1 USE_THREAD=1 USE_OPENMP=0 \
    NUM_THREADS=24 NO_WARMUP=1 NO_AFFINITY=1 CONSISTENT_FPCSR=1 \
    BUILD_LAPACK_DEPRECATED=1 TARGET=PRESCOTT BUFFERSIZE=20 \
    LDFLAGS="-lucrt -static -static-libgcc" \
    COMMON_OPT="-O2 -march=x86-64 -mtune=generic -fno-asynchronous-unwind-tables" \
    FCOMMON_OPT="-O2 -march=x86-64 -mtune=generic -fno-asynchronous-unwind-tables -frecursive -ffpe-summary=invalid,zero -fdefault-integer-8" \
    MAX_STACK_ALLOC=2048 INTERFACE64=1 SYMBOLSUFFIX=64_
tr '\\' '/' < ../procgen-openblas-modified-quadmath.map | grep -Fq 'build/quadmath/.libs/libquadmath.a'
grep -Fq 'procgen_quadmath_relink_probe' ../procgen-openblas-modified-quadmath.map
