#!/bin/bash

#
# Gather realworld data and visualize coverage data.
#

if [ $# -lt 1 ]; then
  echo "<RUN>: <DATA_DIR>"
  exit 1
fi

# Catch arg
DATA_DIR="$1"
pushd "$DATA_DIR" || exit 1
  DATA_DIR="$PWD"
popd || exit 1

# Locate input csv and output dir
RES_DIR="$DATA_DIR/_results"
CSV_PATH="$RES_DIR/data.csv"
echo "DATA_DIR=$DATA_DIR"

# Locate this dir
CUR_DIR=$(dirname "$0")
pushd "$CUR_DIR" || exit 1
  CUR_DIR="$PWD"
popd || exit 1

# Locate python scripts
EXTRACT_DATA_PY="$CUR_DIR/extract_data.py"
PLOT_TREND_PY="$CUR_DIR/plot_cov_trend.py"
PLOT_DISTRIB_PY="$CUR_DIR/plot_cov_distrib.py"
PLOT_OVERHEAD_PY="$CUR_DIR/plot_dipri_overhead.py"
RANK_COV_PY="$CUR_DIR/rank_by_cov.py"

###############
# Run scripts #
###############

echo "python3 $EXTRACT_DATA_PY -f $DATA_DIR -g 900 -u 82800"
python3 "$EXTRACT_DATA_PY" -f "$DATA_DIR" -g 900 -u 82800

echo "python3 $RANK_COV_PY -d $CSV_PATH"
python3 "$RANK_COV_PY" -d "$CSV_PATH"

echo "python3 1 $PLOT_TREND_PY $CSV_PATH $RES_DIR"
python3 "$PLOT_TREND_PY" 1 "$CSV_PATH" "$RES_DIR"

echo "python3 $PLOT_DISTRIB_PY $CSV_PATH $RES_DIR"
python3 "$PLOT_DISTRIB_PY" "$CSV_PATH" "$RES_DIR"

echo "python3 $PLOT_OVERHEAD_PY $CSV_PATH $RES_DIR"
python3 "$PLOT_OVERHEAD_PY" "$CSV_PATH" "$RES_DIR"
