# Setup experimental environments
WORKING_DIR="/root/isefuzz/dipri"
export AFLPP="$WORKING_DIR/aflpp-dipri"   # make source-only
export SEEDS="$AFLPP/testcases"

# Check settings
echo "AFLPP=$AFLPP"
echo "SEEDS=$SEEDS"

# Modify system dump
echo "Modify system dump: echo core > /proc/sys/kernel/core_pattern"
echo "core" > /proc/sys/kernel/core_pattern

# Set DIPRI envs
export DIPRI_MODE="P"
export DIPRI_MEASURE="E"

echo "DIPRI_MODE=$DIPRI_MODE"
echo "DIPRI_MEASURE=$DIPRI_MEASURE"

unset DIPRI_EVAL_TYPE
