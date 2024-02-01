import argparse
import os
import numpy as np
import pandas as pd

from common import targets
from extract_pick_percent_data import configs, parse_rnd_time, parse_pick_percent_one

def dict_to_ave_percentage(pdict: dict) -> float:
    _percents = [_v['pick_percent'] for _k, _v in pdict.items()]
    return np.average(_percents)


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build command line argument parser.
    :return: Arg parser instance.
    """
    _p = argparse.ArgumentParser()
    _p.add_argument('--fuzzdata_dir', '-f', required=True, type=str,
                    help='Path to the fuzz data directory preserving plot_data files.')
    _p.add_argument('--time_gap', '-g', required=False, type=int, default=900,
                    help='Edge-recording time gap in seconds, default is 900.')
    _p.add_argument('--time_upper', '-u', required=False, type=int, default=82800,
                    help='The upper bound of fuzzing time in seconds, default is 82800 (23hour).')
    return _p


if __name__ == '__main__':

    # Parse command.
    parser = build_arg_parser()
    args = parser.parse_args()
    print(args)

    # Parse args.
    fd_dir = os.path.abspath(args.fuzzdata_dir)
    time_gap = args.time_gap
    time_upper = args.time_upper

    # Prepare _results dir
    res_dir = os.path.join(fd_dir, '_results')
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)

    # Extract and gather covered edge from each plot_data file
    ext_data = {
        'fuzzer': [],
        'benchmark': [],
        'trial_id': [],
        'ave_dipri_pick_percent': []
    }
    for fn in sorted(os.listdir(fd_dir)):
        if fn not in configs:
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
                print(fn, fn1, fn2)
                # 'trial_id' refers to as the index of campaign.
                # trial_id = fn2.split('-')[-1]
                trial_id = fn2.split('-')[-1] + '111'
                # Locate dipri_log
                trial_data_dir = os.path.join(fuzzer_target_dir, fn2, 'default')
                pd_path = os.path.join(trial_data_dir, 'plot_data')
                log_path = os.path.join(trial_data_dir, 'dipri_log')
                time_rnd = parse_rnd_time(pd_path, time_gap, time_upper)
                if len(time_rnd) == 0:
                    continue
                rnd_pick_percent = parse_pick_percent_one(log_path)
                ave_percent = dict_to_ave_percentage(rnd_pick_percent)
                # Add into all data
                ext_data['fuzzer'].append(fuzzer)
                ext_data['benchmark'].append(target)
                ext_data['trial_id'].append(trial_id)
                ext_data['ave_dipri_pick_percent'].append(ave_percent)
            # Log
            print('---------------------------------------')
    # Output to local
    csv_path = os.path.join(res_dir, 'dipri_ave_pick_percent.csv')
    df = pd.DataFrame(ext_data)
    df.to_csv(csv_path)
    print(df)
    print('Output to:' + csv_path)