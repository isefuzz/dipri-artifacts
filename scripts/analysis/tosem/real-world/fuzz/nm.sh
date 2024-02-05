#!/bin/bash

# Parameter checking
if [ $# -lt 4 ]; then
  echo "<CAMPAIGN>: <BENCH> <DUR_SEC> <START_IDX> <END_IDX>"
  exit 1
fi

# Global configurations
FUZZER="$AFLPP/afl-fuzz"
TARGET="nm-new"

# Configure arguments
BENCH="$1"
pushd "$BENCH" || exit 1
  BENCH="$PWD"
popd || exit 1
DURATION=$2
START_IDX="$3"
END_IDX="$4"

# Set binary and outputs
TARGET_DIR="$BENCH/$TARGET"
TARGET_PATH="$TARGET_DIR/$TARGET"
OUT_PRE="$TARGET_DIR/outs"
if [ ! -d "$OUT_PRE" ]; then
  mkdir -p "$OUT_PRE"
fi

# Prepare initial seeds. Use afl++ testcases
IN_DIR="$TARGET_DIR/in"
if [ -d "$IN_DIR" ]; then
  rm -rf "$IN_DIR"
fi
mkdir -p "$IN_DIR"
cp "$SEEDS"/others/elf/*.elf "$IN_DIR"

# Start fuzzing
for idx in $(seq "$START_IDX" "$END_IDX"); do

  # Prepare out directories for fuzzing
  OUT_DIR="$OUT_PRE/out-$idx"
  if [ -d "$OUT_DIR" ]; then
    rm -rf "$OUT_DIR"
  fi
  mkdir -p "$OUT_DIR"

  # Run fuzzing.
  "$FUZZER" -V "$DURATION" -i "$IN_DIR" -o "$OUT_DIR" "$TARGET_PATH" @@

done


