import os
import sys
import pandas as pd

from common import *

"""
Visualize the distribution of coverage with box plots
"""


def group_final_cov(df: pd.DataFrame) -> dict:
    """
    Group the final covered edges achieved by each fuzzer in all campaigns
    :param df:
    :return:
    """
    # str -> _inner_dict, key is bench, values are data grouped by fuzzers
    _dict = {}
    _last_tp = df['time'].drop_duplicates().to_numpy()[-1]
    _fuzzers = df['fuzzer'].drop_duplicates().to_numpy()
    _benchmarks = df['benchmark'].drop_duplicates().to_numpy()
    # Start to parse
    for _bench in _benchmarks:
        _inner_dict = {}
        for _fuzzer in colors:
            if _fuzzer not in _fuzzers:
                continue
            _last_edges = df.loc[(df['fuzzer'] == _fuzzer) &
                                 (df['benchmark'] == _bench) &
                                 (df['time'] == _last_tp)]['edges_covered']
            _inner_dict[_fuzzer] = _last_edges.to_numpy()
        _dict[_bench] = _inner_dict
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
    # _ax.set_ylabel('Final Code Coverage')
    _ax.set_ylabel('Final Branch Coverage')
    plt.xticks([])
    # Set colors, label is the name of fuzzer
    for _patch, _label in zip(_bplot['boxes'], data.keys()):
        _patch.set_facecolor(colors[_label])
    # Output
    _path = os.path.join(fdir, f'boxplot-{fbench}.pdf')
    output_fig(_fig, _path)


def main(cov_csv: str, out_dir: str):
    # Create dir to preserve figure
    fig_dir = os.path.join(out_dir, 'fig_covbox')
    if not os.path.exists(fig_dir):
        os.mkdir(fig_dir)
    # Read cov_csv
    print('Draw boxplot...')
    cov_df = pd.read_csv(cov_csv)
    plot_dict = group_final_cov(cov_df)
    for benchmark in plot_dict:
        bench_dict = plot_dict[benchmark]
        try:
            plot_distrib_and_output(bench_dict, benchmark, fig_dir)
        except ValueError:
            print('[WARN] Skip benchmark:', benchmark)
            print([(k, len(v)) for k, v in bench_dict.items()])


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: <this_script> <cov_csv> <out_dir>')
        sys.exit(1)

    # Parse arg
    main(cov_csv=os.path.abspath(sys.argv[1]),
         out_dir=os.path.abspath(sys.argv[2]))
