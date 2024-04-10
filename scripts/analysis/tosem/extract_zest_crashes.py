import argparse
import os
import pandas as pd

from datetime import datetime
from common import *

def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build command line argument parser.
    :return: Arg parser instance.
    """
    _p = argparse.ArgumentParser()
    _p.add_argument('--fuzzdata_dir', '-f', required=True, type=str,
                    help='Path to the fuzz data directory preserving plot_data files.')
    return _p

def parse_fuzz_log(path:str,dictionary:dict):
    with open(path) as f:
        for line in f:
            if line.startswith("Found crash:"):
                crash_found = line.split(' ')[3]
                if crash_found in dictionary:
                    dictionary[crash_found] += 1
                else:
                    dictionary[crash_found] = 1

if __name__ == '__main__':
    # build arg parser.
    parser = build_arg_parser()
    args = parser.parse_args()
    print(args)

    # get args.
    fd_dir = os.path.abspath(args.fuzzdata_dir)

    # Prepare _results dir
    res_dir = os.path.join(fd_dir, '_results'+datetime.now().strftime("%Y-%m-%d"))
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)

    # Extract and gather crashes from each fuzz.log file
    crash_info = {
        'fuzzer': [],
        'target': [],
        'trail':[],
        'crash': [],
        'num': []
    }

    outs = [f'out-{_}' for _ in range(10)]
    for fn in sorted(os.listdir(fd_dir)):
        if fn not in fuzzers:
            continue
        fuzzer = fn         # yd: get fuzzer information.
        fuzzer_dir = os.path.join(fd_dir, fn)
        # fuzzer x target -> campaign config
        for fn1 in sorted(os.listdir(fuzzer_dir)):
            if fn1 not in targets_zest:
                continue
            target = fn1    # yd: get target information
            fuzzer_target_dir = os.path.join(fuzzer_dir, target)
            # Traverse each campaign dir
            for fn2 in sorted(os.listdir(fuzzer_target_dir)):
                if fn2 not in outs:
                    continue
                trial_id = fn2.split('-')[-1]
                # Log
                print(fn, fn1, fn2)
                # Locate fuzz.log
                dictionary = dict()
                fuzzlog_path = os.path.join(fuzzer_target_dir, fn2, 'fuzz.log')
                parse_fuzz_log(fuzzlog_path,dictionary)
                for crash in dictionary:
                    crash_info['fuzzer'].append(fuzzer)
                    crash_info['target'].append(target)
                    crash_info['trail'].append(trial_id)
                    crash_info['crash'].append(crash)
                    crash_info['num'].append(dictionary[crash])
            # Log
            print('---------------------------------------')
    # Output to local
    csv_name = f'crash_data.csv'
    csv_path = os.path.join(res_dir, csv_name)  # Maybe data.csv, TBD
    df = pd.DataFrame(crash_info)
    df.to_csv(csv_path)
    print(df)
    print('Output to:' + csv_path)