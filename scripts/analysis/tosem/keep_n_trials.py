import sys
import os
import pandas as pd



def reassign_trial_ids(ori_df: pd.DataFrame) -> pd.DataFrame:
    _data = []
    _trial_id = 0
    for _row in ori_df.to_numpy():
        _tp = _row[-5]
        if _tp == 0:
            _trial_id += 1
        _row[-6] = _trial_id
        _data.append(_row)
    return pd.DataFrame(data=_data, columns=ori_df.columns)

def remove_stillborn_and_keep_n_trials(
        ori_df: pd.DataFrame,
        tupper: int, N: int
) -> pd.DataFrame:
    _data = []
    _camp_trial_cnt_dict = dict()
    _fuzzers = ori_df['fuzzer'].drop_duplicates().to_numpy()
    _benchmarks = ori_df['benchmark'].drop_duplicates().to_numpy()
    for _fuzzer in _fuzzers:
        _camp_trial_cnt_dict[_fuzzer] = dict()
        for _benchmark in _benchmarks:
            _camp_trial_cnt_dict[_fuzzer][_benchmark] = 0
            _camp_data = ori_df.loc[(ori_df['fuzzer'] == _fuzzer) &
                                    (ori_df['benchmark'] == _benchmark)]
            _trial_ids = _camp_data['trial_id'].drop_duplicates().to_numpy()
            for _trial_id in _trial_ids:
                _trial_data = _camp_data.loc[_camp_data['trial_id'] == _trial_id]
                _last_tp = _trial_data['time'].to_numpy()[-1]
                if _last_tp < tupper:
                    # This is a stillborn trial, deprecate it
                    print('[LOG] Stillborn:', _fuzzer, _benchmark, _trial_id, _last_tp)
                    continue
                elif _camp_trial_cnt_dict[_fuzzer][_benchmark] < N:
                    # Only keep N trials
                    _data.extend(_trial_data.to_numpy())
                    _camp_trial_cnt_dict[_fuzzer][_benchmark] += 1
    return pd.DataFrame(data=_data, columns=ori_df.columns)


if __name__ == '__main__':

    if len(sys.argv) != 5:
        print('Usage: <this_script> <data_csv> <time_upper> <n_trial> <rewrite>')
        sys.exit(1)

    # Parse arg
    data_csv = os.path.abspath(sys.argv[1])
    time_upper = int(sys.argv[2])
    n_trial = int(sys.argv[3])
    rewrite = bool(int(sys.argv[4]))

    # Read in data_csv
    df = pd.read_csv(data_csv, index_col=0)
    # Reassign trial_ids first
    df = reassign_trial_ids(ori_df=df)
    # Remove still born trials
    df = remove_stillborn_and_keep_n_trials(ori_df=df, tupper=time_upper, N=n_trial)
    # Check
    fuzzers = df['fuzzer'].drop_duplicates().to_numpy()
    benchmarks = df['benchmark'].drop_duplicates().to_numpy()
    for fuzzer in fuzzers:
        for benchmark in benchmarks:
            camp_data = df.loc[(df['fuzzer'] == fuzzer) & (df['benchmark'] == benchmark)]
            print(fuzzer, benchmark, len(camp_data['trial_id'].drop_duplicates().to_numpy()))
    # Rewrite
    if rewrite:
        print('[LOG] Rewrite:', data_csv)
        df.to_csv(data_csv)
