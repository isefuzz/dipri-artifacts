import sys
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

from plot_dipri_overhead import size_dict

def group_last_dipri_overhead(df: pd.DataFrame, last_tp=82800):
    _fuzzers = df['fuzzer'].drop_duplicates().to_numpy()
    _cols = ['benchmark', 'dipri_rnd', 'dipri_time_percent']
    _data = dict()
    for _fuzzer in _fuzzers:
        _row = df.loc[(df['fuzzer'] == _fuzzer) &
                      (df['time'] == last_tp)][_cols]
        _data_with_size = []
        for _elem in _row.to_numpy():
            _di = dict(target=_elem[0], dipri_rnd=_elem[1],
                       real_map_size=size_dict[_elem[0]],
                       dipri_time_percent=_elem[2])
            _data_with_size.append(_di)
        _data[_fuzzer] = _data_with_size
    return _data


def cal_pcc(x_true, y_true) -> float:
    _a, _b = np.polyfit(x_true, y_true, deg=1)
    _y_pred = _a * x_true + _b
    return r2_score(y_true=y_true, y_pred=_y_pred)

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: <this_script> <data_csv> <out_dir>')
        sys.exit(1)

    # Read in args
    data_csv = os.path.abspath(sys.argv[1])
    out_dir = os.path.abspath(sys.argv[2])

    # Read in csv
    data_group_by_fuzzer = group_last_dipri_overhead(df=pd.read_csv(data_csv, index_col=0))
    cols = ['real_map_size', 'dipri_rnd', 'dipri_time_percent']
    for fuzzer in data_group_by_fuzzer:
        print(fuzzer)
        data = pd.DataFrame(data=data_group_by_fuzzer[fuzzer])[cols]
        print(data.corr())
        print('-------------------------------------------------------')
    vh_data = pd.DataFrame(data=data_group_by_fuzzer['dipri-VH'])
    vh_data = vh_data.loc[(vh_data['target'] == 'readelf') |
                          (vh_data['target'] == 'mjs') |
                          (vh_data['target'] == 'xmllint')]
    print(vh_data[cols].corr())
