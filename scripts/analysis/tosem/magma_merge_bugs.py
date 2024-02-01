import argparse
import os
import json
import shutil

import pandas as pd


projects = ['libpng','libtiff','libxml2','libsndfile','lua','sqlite3']


"""
Aggregate the bugs.json report by magma into one csv
"""

def locate_bugs_json(root_dir: str) -> list:
    _bugs_jsons = set()
    _folder_stack = [root_dir]
    while len(_folder_stack) != 0:
        _dir = _folder_stack.pop()
        for _fn in os.listdir(_dir):
            _path = os.path.join(_dir, _fn)
            if 'bugs.json' == _fn:
                _bugs_jsons.add(_path)
            elif os.path.isdir(_path):
                _folder_stack.append(_path)
    return sorted(list(_bugs_jsons))


def parse_bugs_dict(bugs: dict, timestamp: float, trial_offset: int = 0) -> tuple:
    """
    Parse bugs.json into a dataframe
    """
    _data = []
    _results = bugs['results']
    _trial_cnt = 1
    _relative_trial = None
    for _fuzzer in _results:
        for _project in _results[_fuzzer]:
            if _project not in projects:
                # Concentrate on all finished projects
                continue
            for _target in _results[_fuzzer][_project]:
                for _trial in _results[_fuzzer][_project][_target]:
                    _relative_trial = trial_offset + _trial_cnt
                    _trial_cnt += 1
                    # Find type is one of ['reached', 'triggered']
                    for _findtype in _results[_fuzzer][_project][_target][_trial]:
                        for _bugid in _results[_fuzzer][_project][_target][_trial][_findtype]:
                            _time2bug = _results[_fuzzer][_project][_target][_trial][_findtype][_bugid]
                            _data.append(dict(trial_id=_relative_trial, project=_project,
                                              fuzzer=_fuzzer, target=_target, find_type=_findtype,
                                              bug=_bugid, time=_time2bug, timestamp=timestamp))
    return pd.DataFrame(data=_data), _relative_trial


def load_json_as_dict(path: str) -> dict:
    with open(path, 'r') as _jfile:
        return json.load(_jfile)


def trimming_bugs(bugs:pd.DataFrame, N: int) -> pd.DataFrame:
    """
    Trimming by specific bugs
    """
    _dfs = []
    for _fuzzer in bugs['fuzzer'].drop_duplicates():
        for _bug in bugs['bug'].drop_duplicates():
            for _type in bugs['find_type'].drop_duplicates():
                _bug_data = bugs.loc[(bugs['fuzzer'] == _fuzzer) &
                                      (bugs['bug'] == _bug) &
                                      (bugs['find_type'] == _type)]
                _abs_n_trial = _bug_data['trial_id'].drop_duplicates().size
                if _abs_n_trial <= N:
                    _dfs.append(_bug_data)
                    continue
                print(_fuzzer, _bug, _abs_n_trial, _bug_data['timestamp'].drop_duplicates().to_list())
                # Sort by the timestamp put at [-1]
                _trimmed_data = sorted(_bug_data.to_numpy(), key=lambda x:x[-1], reverse=True)[:N]
                _dfs.append(pd.DataFrame(_trimmed_data, columns=bugs.columns))
    return pd.concat(_dfs, ignore_index=True)

def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build command line argument parser.
    :return: Arg parser instance.
    """
    _p = argparse.ArgumentParser()
    _p.add_argument('--data_dir', '-d', required=True, type=str,
                    help='Path to the directory preserving bugs.json files.')
    _p.add_argument('--n_trial', '-n', required=False, type=int, default=10,
                    help='Preserving n trials for each campaign.')
    return _p


if __name__ == '__main__':
    # Parse command.
    parser = build_arg_parser()
    args = parser.parse_args()
    print(args)

    # Parse args
    data_dir = os.path.abspath(args.data_dir)
    n_trial = args.n_trial

    # Locate all bugs.json
    bugs_json_files = locate_bugs_json(data_dir)
    # Read and parse each
    bug_dfs = []
    last_trial_id = 0
    format1 = '%Y-%m-%d %H:%M:%S'
    for bug_json in sorted(bugs_json_files):
        # Get the last modified time and turn into time stamp
        float_time = os.path.getmtime(bug_json)
        bug_dict = load_json_as_dict(bug_json)
        bug_df, last_trial_id = parse_bugs_dict(bug_dict, float_time, last_trial_id)
        bug_dfs.append(bug_df)
    # Concat all
    bugs_df = pd.concat(bug_dfs, ignore_index=True)
    print('Before trimming:', bugs_df.index.size)
    # bug_df['timestamp'] = pd.to_datetime(bug_df['timestamp'], unit='s').dt.strftime('%Y-%m-%d')
    # Trimming and keeping 10 trials for each camp (fuzzer*target)
    bugs_df = trimming_bugs(bugs_df, n_trial)
    print('After trimming:', bugs_df.index.size)
    # Output to local
    out_dir = os.path.join(data_dir, '_results')
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.mkdir(out_dir)
    bugs_csv = os.path.join(out_dir, 'magma-bugs.csv')
    bugs_df.to_csv(bugs_csv)
    print('Output to:', bugs_csv)
