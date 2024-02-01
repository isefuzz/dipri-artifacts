#!/bin/bash

if [ $# -lt 3 ]; then
  echo "<RUN>: <FUZZER_DIR> <TARGET_DIR> <SHOWMAP_PATH>"
  exit 1
fi

# Parse args
FUZZER_DIR="$1"
TARGET_DIR="$2"
SHOWMAP_PATH="$3"
echo "FUZZER_DIR=$FUZZER_DIR"
echo "TARGET_DIR=$TARGET_DIR"
echo "SHOWMAP_PATH=$SHOWMAP_PATH"

# Locate this dir
CUR_DIR=$(dirname "$0")
pushd "$CUR_DIR" || exit 1
  CUR_DIR="$PWD"
popd || exit 1
# Locate other script under this dir
SHOWMAP_AND_AGGREGATE_PY="$CUR_DIR/showmap_and_aggregate.py"

# All the targets
TARGETS=(
  "cxxfilt" "readelf" "nm-new" "objdump"
  "djpeg" "mjs" "mutool" "xmllint"
)

for TARGET in "${TARGETS[@]}"; do

  # Locate the unified target
  TARGET_PATH="$TARGET_DIR/$TARGET/$TARGET"

  # Run the python script
  echo "python3 $SHOWMAP_AND_AGGREGATE_PY $SHOWMAP_PATH $TARGET_PATH $FUZZER_DIR"
  python3 "$SHOWMAP_AND_AGGREGATE_PY" "$SHOWMAP_PATH" "$TARGET_PATH" "$FUZZER_DIR"

done

