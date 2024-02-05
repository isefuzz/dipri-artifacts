# Setup experimental environments
WORKING_DIR="/root/isefuzz/dipri"
export AFLPP="$WORKING_DIR/AFLplusplus-4.06c"   # make source-only
export SEEDS="$AFLPP/testcases"

# Check settings
echo "AFLPP=$AFLPP"
echo "SEEDS=$SEEDS"

# Modify system dump
echo "Modify system dump: echo core > /proc/sys/kernel/core_pattern"
echo "core" > /proc/sys/kernel/core_pattern

unset DIPRI_MODE
unset DIPRI_MEASURE
