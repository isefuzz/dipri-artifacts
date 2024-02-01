import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from common import colors, output_fig

def plot_ave_pick_percent(data: dict, show_legends: bool) -> plt.Figure:
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
    _ax.set(ylabel='Seed-Picking Ratio (%)')
    # _ax.set(ylabel='% of Picked Seeds')
    # Each line is a fuzzer
    _AX = None
    for _fuzzer in data:
        _fuzzer_data = data[_fuzzer]
        # Drawing
        _X = np.array(_fuzzer_data['time']) / 3600  # Time in hours
        if _AX is None:
            _AX = _X
        # The mean coverage curve line
        _ax.plot(_X, _fuzzer_data['ave_percent'], label=_fuzzer,
                 linewidth=2, alpha=0.8, color=colors[_fuzzer])
        # The in range filling
        # _ax.fill_between(_X, _fuzzer_data['min_percent'], _fuzzer_data['max_percent'],
        #                  alpha=0.3, color=colors[_fuzzer])
    # Set A line
    # _ax.plot(_AX, [100]*93, label='dipri-A', linewidth=2, alpha=0.8, color='black')
    # _ax.plot(_AX, [100]*93, label='dipri-A', linewidth=2, alpha=0.8, color=colors['dipri-AE'])
    # _ax.plot(_AX, [100]*93, label='dipri-A', linewidth=2, alpha=0.8, color=colors['dipri-AH'])
    if show_legends:
        _ax.legend(loc='lower right')
    return _fig


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
            # Record fuzzer performance at each time point
            _fuzzer_dict = {
                'time': [],
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
                _fuzzer_dict['min_percent'].append(_camp_data['dipri_pick_percent'].min())
                _fuzzer_dict['max_percent'].append(_camp_data['dipri_pick_percent'].max())
                _fuzzer_dict['ave_percent'].append(_camp_data['dipri_pick_percent'].mean())
            _inner_dict[_fuzzer] = _fuzzer_dict
        _dict[_bench] = _inner_dict
    return _dict


def plot_and_output(
        data: dict, fbench: str, fdir: str,
        show_legends: bool = False):
    _fig = plot_ave_pick_percent(data, show_legends)
    if show_legends:
        _fpath = os.path.join(fdir, f'dipri-pickpercent-{fbench}-legends.pdf')
    else:
        _fpath = os.path.join(fdir, f'dipri-pickpercent-{fbench}.pdf')
    output_fig(_fig, _fpath)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: <this_script> <data_csv> <out_dir>')
        sys.exit(1)

    # Read in args
    data_csv = os.path.abspath(sys.argv[1])
    out_dir = os.path.abspath(sys.argv[2])

    # Create dir to preserve figure
    fig_dir = os.path.join(out_dir, 'fig_pickpercent')
    if not os.path.exists(fig_dir):
        os.mkdir(fig_dir)
    # Read cov_csv
    data_df = pd.read_csv(data_csv)
    # Draw coverage curves
    print('Plot DiPri picking percentage...')
    plot_dict = group_percent_by_time(data_df)
    for benchmark in plot_dict:
        bench_dict = plot_dict[benchmark]
        # Plot trend
        plot_and_output(bench_dict, benchmark, fig_dir, True)
        plot_and_output(bench_dict, benchmark, fig_dir)
