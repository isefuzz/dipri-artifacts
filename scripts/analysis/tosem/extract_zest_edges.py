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
    _p.add_argument('--time_gap', '-g', required=False, type=int, default=900,
                    help='Edge-recording time gap in seconds, default is 900.')
    _p.add_argument('--time_upper', '-u', required=False, type=int, default=86400,
                    help='The upper bound of fuzzing time in seconds, default is 86400.')
    return _p


def parse_coverage_by_gap(path: str, tgap: int, tupper: int) -> list:
    """
    :param path: the path to plot_data file
    :param tgap: time gap
    :param tupper: time upper
    :return: a list of triples, each triple is (time, covered_edges, total_execs)
    """
    _tuples = []
    _time_points = [_ for _ in range(0, tupper + 1, tgap)]
    _df = pd.read_csv(path,index_col=0, delimiter=', ', engine='python')
    _df = _df[~_df.index.duplicated(keep='first')]
    # print(_df)
    # print(_df.columns)
    # print(_df.iloc[0])
    # start_time = _df.iloc[0].name
    # print(start_time)
    # print(type(_df.iloc[0]['valid_covered_probes']))
    
    for _tp in _time_points:
        _col = None
        if _tp == 0:
            # Special case. Use first non-zero coverage as the coverage at the time point 0.
            _i = 0
            while _i < 900 and _df.iloc[_i]['valid_covered_probes'] == 0:
                _i += 1
                
            _col = _df.iloc[_i]
        elif _tp in _df.index:
            # Use the row if this tp is recorded
            _col = _df.loc[_tp]
        else:
            # Find the closest time point
            _tmp = _tp
            while _tmp and _tmp not in _df.index:
                _tmp -= 1
            # Sanitize check!
            if _tmp == 0:
                raise RuntimeError('Find closest time point failed!')
            _col = _df.loc[_tmp]

        # Extract data
        # print(type(_col['valid_covered_probes']))
        if "dipri_time" not in _col.index:
            _tuples.append((_tp, _col['valid_covered_probes'], _col['all_covered_probes'], _col['total_execs'],_col['execs_per_sec'],0,0.0))
        else:
            _dipri_time_percent = (_col['dipri_time'] /
                                  (_col['dipri_time'] + _col['non_dipri_time'])) * 100
            _tuples.append((_tp, _col['valid_covered_probes'], _col['all_covered_probes'], _col['total_execs'],_col['execs_per_sec'],0,_dipri_time_percent))
        # print('get'+str(_tp))
    return _tuples


if __name__ == '__main__':
    # print(parse_coverage_by_gap("E:\\y1\\seed-prioritization\\out\\outs-11-27\\dipri-AH\\bcel\\out-0\\plot_data",900,86400))
    # Parse command.
    parser = build_arg_parser()
    args = parser.parse_args()
    print(args)

    # Parse args.
    fd_dir = os.path.abspath(args.fuzzdata_dir)
    time_gap = args.time_gap
    time_upper = args.time_upper

    # Prepare _results dir
    res_dir = os.path.join(fd_dir, '_results'+datetime.now().strftime("%Y-%m-%d"))
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)

    # Extract and gather covered edge from each plot_data file
    edge_data = {
        'fuzzer': [],
        'benchmark': [],
        'trial_id': [],
        'time': [],
        'edges_covered': [],
        'all_edges_covered': [],
        'total_execs': [],
        'execs_per_sec': [],
        'dipri_rnd': [],
        'dipri_time_percent': []
    }
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
                if not fn2.startswith('out-'):
                    continue
                # Log
                print(fn, fn1, fn2)
                # 'trial_id' refers to as the index of campaign.
                trial_id = fn2.split('-')[-1]          # yd: get trail id information
                # Locate plot_data
                pd_path = os.path.join(fuzzer_target_dir, fn2, 'plot_data')
                time_cov_pairs = parse_coverage_by_gap(pd_path, time_gap, time_upper)
                # Gather
                for pair in time_cov_pairs:
                    edge_data['fuzzer'].append(fuzzer)
                    edge_data['benchmark'].append(target)
                    edge_data['trial_id'].append(trial_id)
                    edge_data['time'].append(pair[0])
                    edge_data['edges_covered'].append(pair[1])
                    edge_data['all_edges_covered'].append(pair[2])
                    edge_data['total_execs'].append(pair[3])
                    edge_data['execs_per_sec'].append(pair[4])
                    edge_data['dipri_rnd'].append(pair[5])
                    edge_data['dipri_time_percent'].append(pair[6])
            # Log
            print('---------------------------------------')
    # Output to local
    csv_name = f'data_{time_gap}_{time_upper}.csv'
    csv_path = os.path.join(res_dir, csv_name)  # Maybe data.csv, TBD
    df = pd.DataFrame(edge_data)
    df.to_csv(csv_path)
    print(df)
    print('Output to:' + csv_path)
