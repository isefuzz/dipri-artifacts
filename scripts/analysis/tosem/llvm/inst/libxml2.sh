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
export CC=clang
export CXX=clang++
export CFLAGS="-fprofile-instr-generate -fcoverage-mapping"
export CXXFLAGS="-fprofile-instr-generate -fcoverage-mapping"

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
  ./autogen.sh
  ./configure --disable-shared
  make clean
  make -j "$(nproc)" xmllint
popd || exit 1

# Move to target directory

TARGET="xmllint"
TARGET_DIR="$BENCH_DIR/$TARGET"
# Refresh
if [ -d "$TARGET_DIR" ]; then
  rm -rf "$TARGET_DIR"
fi
mkdir -p "$TARGET_DIR"
mv "$SUBJECT_DIR/$TARGET" "$TARGET_DIR"
