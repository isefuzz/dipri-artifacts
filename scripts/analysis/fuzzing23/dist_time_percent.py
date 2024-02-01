import os.path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from fuzzdata import c_targets, dist_family, output_fig

"""
To depict the percentage of time consumed by distance calculation
"""

# plt.rcParams['font.family'] = 'Monospace'   # Set plot style. Use monospaced fonts
plt.rcParams['font.size'] = 16
# plt.rc('ytick', labelsize=12)


def survey(_df: pd.DataFrame):
    _labels = []
    _target_map = {
        'cxxfilt': 'T1',
        'objdump': 'T2',
        'readelf': 'T3',
        'xmllint': 'T4',
    }
    for _idx in _df.index:
        if _idx in _target_map:
            _labels.append(_target_map[_idx])
        else:
            _labels.append(_idx)
    _legends = ['%DIPRI-TIME', '%OTHER-TIME']
    _data = _df.to_numpy()
    _data_cum = _data.cumsum(axis=1)
    # _colormap = 'bwr'
    # _colormap = 'RdGy'
    _colormap = 'RdBu'
    _colors = plt.colormaps[_colormap](
        np.linspace(0.15, 0.85, _data.shape[1]))

    _height = 0.9
    _figsize = (8.0, 4.5)
    _fig, _ax = plt.subplots(figsize=_figsize)
    _ax.invert_yaxis()
    _ax.xaxis.set_visible(False)
    _ax.set_xlim(0, np.sum(_data, axis=1).max())

    for i, (_colname, _color) in enumerate(zip(_legends, _colors)):
        _widths = _data[:, i]
        _starts = _data_cum[:, i] - _widths
        _rects = _ax.barh(_labels, _widths, left=_starts, height=_height, label=f'{_colname}', color=_color)

        r, g, b, _ = _color
        _text_color = 'white'
        # _ax.bar_label(_rects, label_type='center', color=_text_color)
        for _rect in _rects:
            print(_rect)
        if _colname == '%OTHER-TIME':
            _ax.bar_label(_rects, label_type='center', color=_text_color)
    # _ax.legend(ncols=len(_legends), bbox_to_anchor=(0, 1), loc='center left')

    return _fig, _ax


if __name__ == '__main__':
    # Parse argument
    root_dir = os.path.abspath(sys.argv[1])
    results_dir = os.path.join(root_dir, '_results')
    figs_dir = os.path.join(results_dir, 'figs')

    # Find all plot_data
    cols = ['dist_time', 'non_dist_time']
    measures = ['H', 'J']
    modes = ['V', 'A', 'P']
    confs = ['VH', 'VJ', 'AH', 'AJ', 'PH', 'PJ']
    all_idx = measures + modes + confs + c_targets
    all_df = pd.DataFrame(data=np.zeros((len(all_idx), len(cols))), columns=cols, index=all_idx, dtype=int)
    for dist_appr in dist_family:
        for target in tqdm(c_targets, desc=f'For sel-appr {dist_appr}'):
            outs_dir = os.path.join(root_dir, dist_appr, target, 'outs')
            # Traverse each out
            for fn in sorted(os.listdir(outs_dir)):
                if not fn.startswith('out-'):
                    continue
                pd_path = os.path.join(outs_dir, fn, 'default', 'plot_data')
                df = pd.read_csv(pd_path, delimiter=', ', engine='python')[['dist_time', 'non_dist_time']]
                last_row = df.iloc[-1]
                for idx in all_idx:
                    if (idx in dist_appr) or (idx == target):
                        all_df.loc[idx] += last_row.copy()
    # Cal other times
    all_df['sum_time'] = all_df['dist_time'] + all_df['non_dist_time']
    for col in cols:
        all_df[f'percent-{col}'] = (all_df[col] / all_df['sum_time']) * 100
        all_df[f'percent-{col}'] = all_df[f'percent-{col}'].round(1)
    csv_path = os.path.join(results_dir, '0-dist-time-percentage.csv')
    print(f'Write csv to {csv_path}')
    all_df.to_csv(csv_path)

    fig, ax = survey(all_df[['percent-dist_time', 'percent-non_dist_time']])
    fig_path = os.path.join(figs_dir, 'dist-time-percent.pdf')
    output_fig(figure=fig, path=fig_path)
