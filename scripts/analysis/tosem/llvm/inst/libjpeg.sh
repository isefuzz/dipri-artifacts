#!/bin/bash

# Parameter checking
if [ $# -lt 2 ]; then
  echo "<BUILD>: <SUBJECT_DIR> <BENCH_DIR>"
  exit 1
fi

# Get abspath to subject directory
SUBJECT_DIR="$1"
pushd "$SUBJECT_DIR" || exit 1
  SUBJECT_DIR="$PWD"
popd || exit 1

# Get abspath to target directory
BENCH_DIR="$2"
pushd "$BENCH_DIR" || exit 1
  BENCH_DIR="$PWD"
popd || exit 1

# Choose compilers
INST_OPT="-fprofile-instr-generate -fcoverage-mapping"
export CC="clang"
export CXX="clang++"
export CFLAGS="$INST_OPT"
export CXXFLAGS="$INST_OPT"

# Show configuration results
echo "==================== CONF-LOG ===================="
echo "SUBJECT_DIR=$SUBJECT_DIR"
echo "BENCH_DIR=$BENCH_DIR"
echo "CC=$CC"
echo "CXX=$CXX"
echo "CFLAGS=$CFLAGS"
echo "CXXFLAGS=$CXXFLAGS"
echo "==================== CONF-LOG ===================="
sleep 3

# Instrument SUBJECT programs
pushd "$SUBJECT_DIR" || exit 1
  rm CMakeCache.txt
  cmake . -G "Unix Makefiles" -DBUILD_SHARED_LIBS=OFF -DBUILD_STATIC_LIBS=ON
  make clean
  make -j "$(nproc)" djpeg
popd || exit 1

# Move to target directory

TARGET="djpeg"
TARGET_DIR="$BENCH_DIR/$TARGET"
# Refresh
if [ -d "$TARGET_DIR" ]; then
  rm -rf "$TARGET_DIR"
fi
mkdir -p "$TARGET_DIR"
mv "$SUBJECT_DIR/$TARGET" "$TARGET_DIR"
# Also move shared object FIXME: Cannot mv. djpeg will access the original built libjpeg.so when executing.
#mv "$SUBJECT_DIR/libjpeg.so"* "$TARGET_DIR"
cp "$SUBJECT_DIR/libjpeg.so" "$TARGET_DIR"
