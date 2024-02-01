import os
import sys
import numpy as np
import pandas as pd

from common import *


def group_cov_by_time(df: pd.DataFrame, draw_exec: bool) -> dict:
    """
    Group edge data by time points
    :param df: dataframe extract from cov_csv
    :param draw_exec: whether draw execution lines
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
            if draw_exec:
                _fuzzer_dict = {
                    'time': [],
                    'min_edges': [],
                    'max_edges': [],
                    'ave_edges': [],
                    'ave_execs': [],
                    'ave_exec_speed': [],
                }
            else:
                _fuzzer_dict = {
                    'time': [],
                    'min_edges': [],
                    'max_edges': [],
                    'ave_edges': [],
                    'ave_exec_speed': [],
                }
            for _tp in _times:
                _camp_data = df.loc[(df['benchmark'] == _bench) &
                                    (df['fuzzer'] == _fuzzer) &
                                    (df['time'] == _tp)]
                # print(_camp_data)
                _fuzzer_dict['time'].append(_tp)
                _fuzzer_dict['min_edges'].append(_camp_data['edges_covered'].min())
                _fuzzer_dict['max_edges'].append(_camp_data['edges_covered'].max())
                _fuzzer_dict['ave_edges'].append(_camp_data['edges_covered'].mean())
                if draw_exec:
                    # Exec speed = (execs_per_sec)
                    _fuzzer_dict['ave_exec_speed'].append(_camp_data['execs_per_sec'].mean())
                    _fuzzer_dict['ave_execs'].append(_camp_data['total_execs'].mean())
            _inner_dict[_fuzzer] = _fuzzer_dict
        _dict[_bench] = _inner_dict
    return _dict


def plot_time_cov_in_range(
        data: dict, xtype: str, show_legends: bool) -> plt.Figure:
    """
    Plot coverage curve along with time.
    :param data: coverage time
    :param xtype: data on x-axis, one of {time, execution}
    :param show_legends: whether show legends, i.e., fuzzer name
    :return:
    """
    # Start to draw
    plt.clf()
    _fig, _ax = plt.subplots(nrows=1, ncols=1, figsize=(5.0, 4.5))
    _ax.grid(color='gray', linestyle='--', linewidth=0.3)
    # Set labels
    if xtype == 'exec':
        _ax.set(xlabel='#Executions')
    else:
        _ax.set(xlabel='Time (Hour)', xticks=[_ * 5 for _ in range(5)])
    _ax.set(ylabel='Valid Edge Coverage')
    # Each line is a fuzzer
    for fuzzer in data:
        _fuzzer_data = data[fuzzer]
        # Drawing
        _X = np.array(_fuzzer_data['time']) / 3600  # Time in hours
        if xtype == 'exec':
            _X = np.array(_fuzzer_data['ave_execs'])
        # The mean coverage curve line
        _ax.plot(_X, _fuzzer_data['ave_edges'], label=fuzzer,
                 linewidth=2, alpha=0.8, color=colors[fuzzer])
        # The in range filling
        _ax.fill_between(_X, _fuzzer_data['min_edges'], _fuzzer_data['max_edges'],
                         alpha=0.3, color=colors[fuzzer])
    if show_legends:
        _ax.legend(loc='lower right')
    return _fig


def plot_exec_speed(data: dict, show_legends: bool) -> plt.Figure:
    """
    Execution speed = execs_per_sec
    """
    # Start to draw
    plt.clf()
    _fig, _ax = plt.subplots(nrows=1, ncols=1, figsize=(5.0, 4.5))
    _ax.grid(color='gray', linestyle='--', linewidth=0.3)
    # Set label
    _ax.set(xlabel='Time (Hour)', xticks=[_ * 5 for _ in range(5)])
    _ax.set(ylabel='Execution Speed')
    # Each line is a fuzzer
    for fuzzer in data:
        _fuzzer_data = data[fuzzer]
        # Drawing
        _X = np.array(_fuzzer_data['time']) / 3600  # Time in hours
        # The mean coverage curve line
        _ax.plot(_X, _fuzzer_data['ave_exec_speed'], label=fuzzer,
                 linewidth=2, alpha=0.8, color=colors[fuzzer])
    if show_legends:
        _ax.legend(loc='lower right')
    return _fig


def plot_trend_and_output(
        data: dict, xtype: str,
        fbench: str, fdir: str,
        show_legends: bool = False):
    _fig = plot_time_cov_in_range(data, xtype, show_legends)
    if show_legends:
        _fpath = os.path.join(fdir, f'{xtype}-cov-{fbench}-legends.pdf')
    else:
        _fpath = os.path.join(fdir, f'{xtype}-cov-{fbench}.pdf')
    output_fig(_fig, _fpath)


def plot_exec_speed_and_output(
        data: dict, fbench: str,
        fdir: str, show_legends: bool = False):
    _fig = plot_exec_speed(data, show_legends)
    if show_legends:
        _fpath = os.path.join(fdir, f'speed-{fbench}-legends.pdf')
    else:
        _fpath = os.path.join(fdir, f'speed-{fbench}.pdf')
    output_fig(_fig, _fpath)


def main(draw_exec: bool, cov_csv: str, out_dir: str):
    # Create dir to preserve figure
    fig_dir = os.path.join(out_dir, 'fig_covtrend')
    if not os.path.exists(fig_dir):
        os.mkdir(fig_dir)
    # Read cov_csv
    cov_df = pd.read_csv(cov_csv)
    # Draw coverage curves
    print('Draw curves...')
    plot_dict = group_cov_by_time(cov_df, draw_exec)
    for benchmark in plot_dict:
        bench_dict = plot_dict[benchmark]
        plot_trend_and_output(bench_dict, 'time', benchmark, fig_dir, True)
        plot_trend_and_output(bench_dict, 'time', benchmark, fig_dir)
        if draw_exec:
            plot_exec_speed_and_output(bench_dict, benchmark, fig_dir, True)
            plot_exec_speed_and_output(bench_dict, benchmark, fig_dir)
            plot_trend_and_output(bench_dict, 'exec', benchmark, fig_dir)


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print('Usage: <this_script> <draw_exec> <cov_csv> <out_dir>')
        sys.exit(1)

    # Parse arg
    main(draw_exec=bool(int(sys.argv[1])),
         cov_csv=os.path.abspath(sys.argv[2]),
         out_dir=os.path.abspath(sys.argv[3]))
