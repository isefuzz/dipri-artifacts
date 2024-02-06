import shutil
import sys
import os
import pandas as pd

from common import *

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage: <this_script> <data_dir> <data_type> <time_upper> <if_del>')
        sys.exit(1)

    # Params
    fd_dir = os.path.abspath(sys.argv[1])
    data_type = sys.argv[2]  # 'plot_data' or 'llvm-cov.csv'
    time_upper = int(sys.argv[3])
    if_del = bool(int(sys.argv[4]))
    print('[LOG] fd_dir', fd_dir)
    print('[LOG] data_type', data_type)
    print('[LOG] time_upper', time_upper)
    print('[LOG] if_del', if_del)

    # Collect still_born trials
    trial_cnt = 0
    stillborn_trials = []
    for fn in sorted(os.listdir(fd_dir)):
        if fn not in fuzzers:
            continue
        fuzzer = fn
        fuzzer_dir = os.path.join(fd_dir, fn)
        # fuzzer x target -> campaign config
        for fn1 in sorted(os.listdir(fuzzer_dir)):
            if fn1 not in targets:
                continue
            target = fn1
            fuzzer_target_dir = os.path.join(fuzzer_dir, target, 'outs')
            if not os.path.exists(fuzzer_target_dir):
                continue
            # Traverse each campaign dir
            for fn2 in sorted(os.listdir(fuzzer_target_dir)):
                if not fn2.startswith('out-'):
                    continue
                # Log
                print('[LOG]', fn, fn1, fn2)
                # 'trial_id' refers to as the index of campaign.
                trial_id = fn2.split('-')[-1]
                # Locate plot_data
                trial_cnt += 1
                trial_dir = os.path.join(fuzzer_target_dir, fn2)
                if data_type == 'plot_data':
                    pd_path = os.path.join(trial_dir, 'default', data_type)
                    # Read last line and parse time
                    with open(pd_path, 'r') as f:
                        last_line = f.readlines()[-1]
                    last_tp = int(last_line.split(',')[0])
                elif data_type == 'llvm-cov.csv':
                    llvm_cov_csv = os.path.join(trial_dir, 'default', data_type)
                    llvm_cov_df = pd.read_csv(llvm_cov_csv)
                    if llvm_cov_df.empty:
                        print('[LOG] Empty llvm-cov, skip and add stillborn:', llvm_cov_csv)
                        stillborn_trials.append((0, trial_dir))
                        continue
                    last_tp = llvm_cov_df['time'].to_numpy()[-1]
                else:
                    raise RuntimeError('Unsupported data_type:', data_type)
                # Locate stillborn according to the last time point
                if last_tp < time_upper:
                    stillborn_trials.append((last_tp, trial_dir))
    # List all still born trials
    for elem in stillborn_trials:
        if if_del:
            print('[LOG] Remove', elem)
            shutil.rmtree(elem[1])
        else:
            print('[LOG] Stillborn:', elem)
    # Log stats
    print('[STATS] Traverse', trial_cnt, 'trials, find', len(stillborn_trials), 'still born trials.')
