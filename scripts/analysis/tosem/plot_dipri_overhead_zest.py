import os
import sys
import numpy as np
import pandas as pd

from common import *


def group_percent_by_time(df: pd.DataFrame) -> dict:
    """
    Group edge data by time points
    :param df: dataframe extract from cov_csv
    :return: the grouped data as _dict
    """
    # str -> _inner_dict, key is bench, values are data grouped by fuzzers
    _dict = {}
    _fuzzers = df['fuzzer'].drop_duplicates().to_numpy()
    _benchmarks = df['benchmark'].drop_duplicates().to_numpy()
    _times = df['time'].drop_duplicates().to_numpy()
    # Start to parse
    for _bench in _benchmarks:
        _inner_dict = {}
        for _fuzzer in _fuzzers:
            if _fuzzer == 'zest':
                continue
            # Record fuzzer performance at each time point
            _fuzzer_dict = {
                'time': [],
                'dipri_rnd_ave': [],
                'min_percent': [],
                'max_percent': [],
                'ave_percent': []
            }
            for _tp in _times:
                _camp_data = df.loc[(df['benchmark'] == _bench) &
                                    (df['fuzzer'] == _fuzzer) &
                                    (df['time'] == _tp)]
                # print(_camp_data)
                _fuzzer_dict['time'].append(_tp)
                _fuzzer_dict['dipri_rnd_ave'].append(_camp_data['dipri_rnd'].mean())
                _fuzzer_dict['min_percent'].append(_camp_data['dipri_time_percent'].min())
                _fuzzer_dict['max_percent'].append(_camp_data['dipri_time_percent'].max())
                _fuzzer_dict['ave_percent'].append(_camp_data['dipri_time_percent'].mean())
            _inner_dict[_fuzzer] = _fuzzer_dict
        _dict[_bench] = _inner_dict
    return _dict


def plot_dipri_time_in_range(data: dict, show_legends: bool) -> plt.Figure:
    """
    Plot coverage curve along with time.
    :param data: coverage time
    :param show_legends: whether show legends, i.e., fuzzer name
    :return:
    """
    # Start to draw
    plt.clf()
    _fig, _ax = plt.subplots(nrows=1, ncols=1, figsize=(5.0, 4.5))
    _ax.grid(color='gray', linestyle='--', linewidth=0.3)
    # Set labels
    _ax.set(xlabel='Time (Hour)', xticks=[_ * 5 for _ in range(5)])
    _ax.set(ylabel='Occupied Time (%)')
    # Each line is a fuzzer
    for _fuzzer in data:
        _fuzzer_data = data[_fuzzer]
        # Drawing
        _X = np.array(_fuzzer_data['time']) / 3600  # Time in hours
        # The mean coverage curve line
        _ax.plot(_X, _fuzzer_data['ave_percent'], label=_fuzzer,
                 linewidth=2, alpha=0.8, color=colors[_fuzzer])
        # The in range filling
        _ax.fill_between(_X, _fuzzer_data['min_percent'], _fuzzer_data['max_percent'],
                         alpha=0.3, color=colors[_fuzzer])
    if show_legends:
        _ax.legend(loc='lower right')
    return _fig


def plot_overhead_and_output(
        data: dict, fbench: str, fdir: str,
        show_legends: bool = False):
    _fig = plot_dipri_time_in_range(data, show_legends)
    if show_legends:
        _fpath = os.path.join(fdir, f'dipri-time-{fbench}-legends.pdf')
    else:
        _fpath = os.path.join(fdir, f'dipri-time-{fbench}.pdf')
    output_fig(_fig, _fpath)


def extract_last_percent(bdict:dict) -> dict:
    _dict = dict()
    for _fuzzer in bdict:
        _dict[_fuzzer] = bdict[_fuzzer]['ave_percent'][-1]
    return _dict


def extract_last_rnd(bdict:dict) -> dict:
    _dict = dict()
    for _fuzzer in bdict:
        _dict[_fuzzer] = bdict[_fuzzer]['dipri_rnd_ave'][-1]
    return _dict

#
#
# def plot_percent_bar(data:dict, show_legend: bool) -> plt.Figure:
#     plt.clf()
#     _width = .5
#     _multiplier = 0
#     # Where each cluster of bars started. Keys are fuzzers
#     _x = np.arange(1)
#     # Canvas
#     _fig, _ax = plt.subplots(figsize=(6.0, 4.5))
#     for _fuzzer, _percents in data.items():
#         # Locate the bar
#         _offset = _width * _multiplier
#         _multiplier += 1
#         _rects = _ax.bar(_x + _offset, _percents, _width,
#                          label=_fuzzer, color=colors[_fuzzer])
#         # Set others
#         _ax.set_ylabel('Mean Occupied Time (%)')
#         _ax.set_xticks([])
#     if show_legend:
#         _ax.legend(loc='upper left', ncols=len(data.keys()))
#     return _fig


# def plot_bar_and_output(
#         data: dict, fbench: str, fdir: str,
#         show_legends: bool = False):
#     _fig = plot_percent_bar(data, show_legends)
#     if show_legends:
#         _fpath = os.path.join(fdir, f'dipri-time-bar-{fbench}-legends.pdf')
#     else:
#         _fpath = os.path.join(fdir, f'dipri-time-bar-{fbench}.pdf')
#     output_fig(_fig, _fpath)

def extract_last_percents(bdict:dict) -> dict:
    _dict = dict()
    for _fuzzer in bdict:
        _dict[_fuzzer] = bdict[_fuzzer]['ave_percent']
    return _dict


def to_std_dict(adict: dict) -> dict:
    _dict = dict()
    for _fuzzer in adict:
        _dict[_fuzzer] = np.array(adict[_fuzzer]).std()
    return _dict

def plot_distrib_and_output(data: dict, fbench: str, fdir: str):
    # plt.rcParams['font.size'] = 24
    # Turn to dataframe
    _df = pd.DataFrame(data)
    # Start to draw
    _fig, _ax = plt.subplots(nrows=1, ncols=1, figsize=(5.0, 4.5))
    _boxprops = dict(linestyle='-', linewidth=1, color='black')
    _whiskerprops = dict(linestyle='-', linewidth=1, color='black')
    _capprops = dict(linestyle='-', linewidth=1, color='black')
    _medianprops = dict(linestyle='-', linewidth=2.5, color='black')
    _flierprops = dict(marker='o', markeredgecolor='black', markeredgewidth=1)
    _bplot = _ax.boxplot(
        _df, patch_artist=True,
        vert=True, labels=data.keys(), flierprops=_flierprops,
        boxprops=_boxprops, whiskerprops=_whiskerprops,
        capprops=_capprops, medianprops=_medianprops
    )
    _ax.set_ylabel('Final Occupied Time (%)')
    plt.xticks([])
    # Set colors, label is the name of fuzzer
    for _patch, _label in zip(_bplot['boxes'], data.keys()):
        _patch.set_facecolor(colors[_label])
    # Output
    _path = os.path.join(fdir, f'dipri-time-boxplot-{fbench}.pdf')
    output_fig(_fig, _path)


if __name__ == '__main__':
    
    if len(sys.argv) != 3:
        print('Usage: <this_script> <data_csv> <out_dir>')
        sys.exit(1)
        
    # Read in args
    data_csv = os.path.abspath(sys.argv[1])
    out_dir = os.path.abspath(sys.argv[2])

    # Create dir to preserve figure
    fig_dir = os.path.join(out_dir, 'fig_overhead')
    if not os.path.exists(fig_dir):
        os.mkdir(fig_dir)
    # Read cov_csv
    data_df = pd.read_csv(data_csv)
    # Draw coverage curves
    print('Plot DiPri overhead...')
    plot_dict = group_percent_by_time(data_df)
    ave_percent_dict = {}
    ave_percent_std_dict = {}
    ave_rnd_dict = {}
    for benchmark in plot_dict:
        bench_dict = plot_dict[benchmark]
        # Plot trend
        plot_overhead_and_output(bench_dict, benchmark, fig_dir, True)
        plot_overhead_and_output(bench_dict, benchmark, fig_dir)
        # Plot bar
        last_percents = extract_last_percents(bench_dict)
        plot_distrib_and_output(last_percents, benchmark, fig_dir)
        ave_percent_std_dict[benchmark] = to_std_dict(last_percents)
