#!/bin/bash

if [ $# -lt 1 ]; then
  echo "<DECOMPRESS-SUBJECTS>: <TARGET_DIR>"
  exit 1
fi

TARGET_DIR="$1"

pushd "$TARGET_DIR" || exit 1

for SUB in *.tar.gz; do
  tar zxvf "$SUB"
done

popd || exit 1

echo "===================================================="

echo "Decompress subjects done."

