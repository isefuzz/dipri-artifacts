import argparse
import os
import pandas as pd

from common import *

"""

Extract covered edges by given time gap. The style of the resultant csv file
is similar to FuzzBench's data.csv. This script focuses on the following
FuzzBench columns:  

  - 'fuzzer': the used fuzzer
  - 'benchmark': the name of the fuzz target
  - 'trial_id': the index of the campaign 
  - 'time': the time point record coverage
  - 'edges_covered': the coverage
  
Besides, we also interesting how dipri's performance, so the resultant csv file 
should also include:

  - 'total_execs': the number of executions at the give time point
  - 'dipri_time_percent': the percentage of time occupied by DiPri
   
"""


def parse_coverage_by_gap(path: str, tgap: int, tupper: int) -> list:
    """
    :param path: the path to plot_data file
    :param tgap: time gap
    :param tupper: time upper
    :return: a list of triples, each triple is (time, covered_edges, total_execs)
    """
    _tuples = []
    _time_points = [_ for _ in range(0, tupper+1, tgap)]
    _df = pd.read_csv(path, index_col=0, delimiter=', ', engine='python')
    # Remove interrupted campaigns
    if (tupper not in _df.index) and (_df.index[-1] < tupper):
        print(f'time_upper {tupper}, last_idx {_df.index[-1]}')
        raise RuntimeError('Find a stillborn campaign, please remove: ' + path)
    for _tp in _time_points:
        _col = None
        if _tp == 0:
            # Special case. Use first coverage (or maybe 0) as the coverage at the time point 0.
            _col = _df.iloc[0]
            # _col = pd.Series(dict(edges_found=0, total_execs=0))
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
        if 'dipri_log_cnt' not in _col.index:
            _tuples.append((_tp, _col['edges_found'], _col['total_execs'],
                            _col['execs_per_sec'], 0, 0.0))
        else:
            _dipri_time_percent = (_col['dipri_time'] /
                                  (_col['dipri_time'] + _col['non_dipri_time'])) * 100
            _tuples.append((_tp, _col['edges_found'], _col['total_execs'],
                        _col['execs_per_sec'], _col['dipri_log_cnt'], _dipri_time_percent))
    return _tuples



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
        'time': [],
        'edges_covered': [],
        'total_execs': [],
        'execs_per_sec': [],
        'dipri_rnd': [],
        'dipri_time_percent': []
    }
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
                print(fn, fn1, fn2)
                # 'trial_id' refers to as the index of campaign.
                trial_id = fn2.split('-')[-1]
                # Locate plot_data
                pd_path = os.path.join(fuzzer_target_dir, fn2, 'default', 'plot_data')
                time_cov_pairs = parse_coverage_by_gap(pd_path, time_gap, time_upper)
                # Gather
                for pair in time_cov_pairs:
                    ext_data['fuzzer'].append(fuzzer)
                    ext_data['benchmark'].append(target)
                    ext_data['trial_id'].append(trial_id)
                    ext_data['time'].append(pair[0])
                    ext_data['edges_covered'].append(pair[1])
                    ext_data['total_execs'].append(pair[2])
                    ext_data['execs_per_sec'].append(pair[3])
                    ext_data['dipri_rnd'].append(pair[4])
                    ext_data['dipri_time_percent'].append(pair[5])
            # Log
            print('---------------------------------------')
    # Output to local
    csv_path = os.path.join(res_dir, 'data.csv')
    df = pd.DataFrame(ext_data)
    df.to_csv(csv_path)
    print(df)
    print('Output to:' + csv_path)
