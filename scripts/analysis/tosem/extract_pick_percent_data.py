import argparse
import os
import pandas as pd

from common import targets

# Do not parse A-mode as it always pick 100% seeds
configs = [
    # 'dipri-AE', 'dipri-AH',
    'dipri-PE', 'dipri-PH',
    'dipri-VE', 'dipri-VH',
]

def parse_pick_percent_one(path: str) -> dict:
    # _data = []
    _data = dict()
    _first = True
    with open(path, 'r') as f:
        for _line in f.readlines():
            if _line.startswith('reorder_cnt'):
                if _first:
                    _first = False
                else:
                    # Indicate a finish of last prioritization
                    # (_dipri_cnt, _queue_cnt, _pick_cnt, _pick_cnt / _queue_cnt)
                    # _data.append(dict(rnd=_dipri_cnt, queue_cnt=_queue_cnt,
                    #                   pick_cnt=_pick_cnt, pick_percent=(_pick_cnt / _queue_cnt) * 100))
                    _ratio = _pick_cnt / _queue_cnt
                    if _ratio > 1:
                        # Reset to 1, A-mode may traverse the queue several times when find no seeds
                        _ratio = 1
                    _data[_dipri_cnt] = dict(queue_cnt=_queue_cnt, pick_cnt=_pick_cnt,
                                             pick_percent=_ratio * 100)
                # Prepare for next round of pri
                _parts = _line.strip().split(', ')
                _dipri_cnt = int(_parts[0].split(' ')[1])
                _queue_cnt = int(_parts[1].split(' ')[1])
                _pick_cnt = 0
            elif _line.startswith('pick_seed'):
                _pick_cnt += 1
    return _data


def parse_rnd_time(path: str, tgap: int, tupper: int) -> list:
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
        # print(f'time_upper {tupper}, last_idx {_df.index[-1]}')
        # raise RuntimeError('Find a stillborn campaign, please remove: ' + path)
        # Skip
        return []
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
        _tuples.append(dict(time=_tp, rnd=_col['dipri_log_cnt']))
    return _tuples


def combine_time_percent(time_data: list, percent_data: dict) -> list:
    _data = []
    for _time_dict in time_data:
        _time = _time_dict['time']
        _rnd = _time_dict['rnd']
        # Locate data at that rnd
        # _percent_dict = percent_data[_rnd]
        _percent_dict = percent_data[_rnd-1]
        _data.append((_time, _percent_dict['pick_percent']))
    return _data


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
        'dipri_pick_percent': []
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
                trial_id = fn2.split('-')[-1]
                # Locate plot_data
                trial_data_dir = os.path.join(fuzzer_target_dir, fn2, 'default')
                pd_path = os.path.join(trial_data_dir, 'plot_data')
                log_path = os.path.join(trial_data_dir, 'dipri_log')
                time_rnd = parse_rnd_time(pd_path, time_gap, time_upper)
                if len(time_rnd) == 0:
                    continue
                rnd_pick_percent = parse_pick_percent_one(log_path)
                time2percents = combine_time_percent(time_rnd, rnd_pick_percent)
                # Add into all data
                for elem in time2percents:
                    ext_data['fuzzer'].append(fuzzer)
                    ext_data['benchmark'].append(target)
                    ext_data['trial_id'].append(trial_id)
                    ext_data['time'].append(elem[0])
                    ext_data['dipri_pick_percent'].append(elem[1])
            # Log
            print('---------------------------------------')
    # Output to local
    csv_path = os.path.join(res_dir, 'dipri_pick_percent.csv')
    df = pd.DataFrame(ext_data)
    df.to_csv(csv_path)
    print(df)
    print('Output to:' + csv_path)

