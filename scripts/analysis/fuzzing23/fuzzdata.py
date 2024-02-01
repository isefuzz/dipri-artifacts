import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

afl_family = ['aflpp', 'aflpp-Z']
zest_family = ['zest']
dist_family = [
    'dist-VH', 'dist-VJ',
    'dist-AH', 'dist-AJ',
    'dist-PH', 'dist-PJ',
]
c_targets = ['cxxfilt', 'objdump', 'readelf', 'xmllint']
java_targets = ['ant', 'bcel', 'closure', 'rhino']
figsize = (5.0, 4.5)
shapes = {                                  # Shapes for lines in figures, each tuple is (<color>,<marker>,<line>)
    'dist-VH': ('red', 'o'),
    'dist-VJ': ('forestgreen', 'D'),
    'dist-AH': ('darkorange', 'o'),
    'dist-AJ': ('royalblue', 'D'),
    'dist-PH': ('sienna', 'o'),
    'dist-PJ': ('olive', 'D'),
    'aflpp': ('black', '^'),
    'aflpp-Z': ('gray', 'v'),
    'zest': ('black', '^'),
}
markevery = 0.05
markersize = 3.5
cline_width = 2                           # Line width for curve
gline_width = 0.5                           # Line width for grid
# plt.rcParams['font.family'] = 'Monospace'   # Set plot style. Use monospaced fonts
plt.rcParams['font.size'] = 16


def get_fuzzers(prog_lang: str) -> list:
    if prog_lang.upper() == 'C':
        return afl_family + dist_family
    elif prog_lang.upper() == 'JAVA':
        return zest_family + dist_family
    raise RuntimeError(f'Unsupported program language: `{prog_lang}`')


def get_targets(prog_lang: str) -> list:
    if prog_lang.upper() == 'C':
        return c_targets
    elif prog_lang.upper() == 'JAVA':
        return java_targets
    raise RuntimeError(f'Unsupported program language: `{prog_lang}`')


def parse_x_data(prog_lang: str, df: pd.DataFrame, x_name: str):
    _X = None
    if prog_lang.upper() == 'C':
        if x_name == 'time':
            _X = df.index / 3600  # Default in hours
        elif x_name == 'execution':
            _X = df['total_execs']
    elif prog_lang.upper() == 'JAVA':
        if x_name == 'time':
            _X = df.index / 3600  # Default in hours
        elif x_name == 'execution':
            _X = df['# numTrials']
    else:
        raise RuntimeError(f'Unsupported program language: `{prog_lang}`')
    return _X


def parse_y_data(prog_lang: str, df: pd.DataFrame, y_name: str):
    _Y = None
    if prog_lang.upper() == 'C':
        if y_name == 'coverage':
            _Y = df['edges_found']
        elif y_name == 'crash':
            _Y = df['saved_crashes']
    elif prog_lang.upper() == 'JAVA':
        if y_name == 'coverage':
            # _Y = df['all_cov']
            _Y = df['valid_cov']
        elif y_name == 'crash':
            _Y = df['unique_crashes']
    else:
        raise RuntimeError(f'Unsupported program language: `{prog_lang}`')
    return _Y


def parse_x_label(prog_lang: str, x_name: str) -> str:
    c_xlab_map = {
        'time': 'Time (Hours)',
        'execution': '#Executions',
    }
    java_xlab_map = {
        'time': 'Time (Hours)',
        'execution': '#Trials',
    }
    if prog_lang.upper() == 'C':
        return c_xlab_map[x_name]
    elif prog_lang.upper() == 'JAVA':
        return java_xlab_map[x_name]
    raise RuntimeError(f'Unsupported program language: `{prog_lang}`')


def parse_y_label(prog_lang: str, y_name: str) -> str:
    c_ylab_map = {
        'coverage': '#Edges',
        'crash': '#Crashes',
    }
    java_ylab_map = {
        'coverage': '#Valid Edges',
        'crash': '#Crashes',
    }
    if prog_lang.upper() == 'C':
        return c_ylab_map[y_name]
    elif prog_lang.upper() == 'JAVA':
        return java_ylab_map[y_name]
    raise RuntimeError(f'Unsupported program language: `{prog_lang}`')


def draw_fuzz_plot(prog_lang: str, df_dict: dict,
                   x_name: str = 'time', y_name: str = 'coverage', show_legend: bool = False) -> Figure:
    plt.clf()
    _fig, _ax = plt.subplots(1, 1, figsize=figsize)
    _y_min = 1000000000
    _y_max = 0
    _xy_dict = {}
    _fuzzers = get_fuzzers(prog_lang=prog_lang)
    for _fuzzer in _fuzzers:
        if _fuzzer not in df_dict:
            continue
        # Prepare data
        _X = parse_x_data(prog_lang, df_dict[_fuzzer], x_name)
        _Y = parse_y_data(prog_lang, df_dict[_fuzzer], y_name)
        _y_min = min(_y_min, _Y[_Y > 0].min())
        _y_max = max(_y_max, _Y.max())
        # if y_name == 'coverage':
        #     print(y_name, _y_min)
        # Add into xy dict. Later to replace 0 with global min value
        _xy_dict[_fuzzer] = (_X, _Y)
    for _fuzzer in _xy_dict:
        _X = _xy_dict[_fuzzer][0]
        _Y = _xy_dict[_fuzzer][1]
        # if y_name == 'coverage':
        #     print(_Y.replace(to_replace=0, value=_y_min))
        # Draw graph
        _fuzzer_label = str(_fuzzer).upper()
        _ax.plot(_X, _Y.replace(to_replace=0, value=_y_min),
                 label=_fuzzer_label, linewidth=cline_width,
                 markevery=markevery, markersize=markersize,
                 color=shapes[_fuzzer][0], marker=shapes[_fuzzer][1])
        # _ax.plot(_X, _Y.replace(to_replace=0, value=_y_min),
        #          label=_fuzzer_label, linewidth=cline_width,
        #          color=shapes[_fuzzer][0], linestyle=shapes[_fuzzer][1])
    # Set axis
    _ax.set(xlabel=parse_x_label(prog_lang, x_name), ylabel=parse_y_label(prog_lang, y_name))
    _ax.grid(color='grey', linestyle='--', linewidth=gline_width)
    if show_legend:
        _ax.legend(loc='lower right')  # May not use
    if x_name == 'time':
        _ax.set_ylim([_y_min-50, _y_max+100])
        _x_major = MultipleLocator(4)
        _x_major_fmt = FormatStrFormatter('%d')
        _ax.xaxis.set_major_locator(_x_major)
        _ax.xaxis.set_major_formatter(_x_major_fmt)
    return _fig


def parse_df_columns(prog_lang: str) -> list:
    if prog_lang.upper() == 'C':
        _columns = ['# relative_time', 'saved_crashes', 'saved_hangs', 'total_execs', 'edges_found']
    elif prog_lang.upper() == 'JAVA':
        _columns = ['relative_time', 'unique_crashes', '# numTrials', 'all_cov', 'valid_cov']
    else:
        raise RuntimeError(f'Unsupported program language: `{prog_lang}`')
    return _columns


def average_plot_data(prog_lang: str, outs_dir: str, delim: str = ', ', total_secs=86400):
    _columns = parse_df_columns(prog_lang)
    _time_col = _columns[0]
    _pd_cnt = 0
    _sum_df = None
    for fn in sorted(os.listdir(outs_dir)):
        out_dir = os.path.join(outs_dir, fn)
        if fn.startswith('.') or (not os.path.isdir(out_dir)):
            continue
        # Locate plot_data
        _pd_path = os.path.join(out_dir, 'default', 'plot_data')
        _df = pd.read_csv(_pd_path, delimiter=delim, engine='python')
        if prog_lang.upper() == 'JAVA':
            if 'unix_time' in _df.columns:
                # Correct and add 'all_cov' colunm
                _df['all_cov'] = _df['all_covered_probes']
                _df['valid_cov'] = _df['valid_covered_probes']
                # Zest result. Add 'relative_time' column
                _unix_tps = _df['unix_time'].to_numpy()
                _last_tp = _unix_tps[0]
                _relative_tps = []
                for _i in range(len(_unix_tps)):
                    _rtp = _unix_tps[_i] - _last_tp
                    _relative_tps.append(_rtp)
                # print(_relative_tps)
                _df['relative_time'] = pd.Series(data=_relative_tps)
                # Splice
                _df = _df[_columns]
            else:
                # Zest-Dist results, splice and turn ms into seconds.
                # Trim out unused cols
                _df = _df[_columns]
                # Turn into seconds
                _df[_time_col] = _df[_time_col] / 1000
                _df = _df.astype({_time_col: 'int'})
        else:
            # C
            _df = _df[_columns]
        _df = _df.drop_duplicates()
        # Get relative end time point
        _end_tp = _df.index[-1]
        _all_tps = [_tp for _tp in range(_end_tp + 1)]
        # We fill up missing time point with the data of the last row.
        # Set the first row as all zeros.
        _last_row = np.zeros(len(_df.columns))
        # Create new data dict
        _new_data = []
        for _tp in tqdm(range(total_secs + 1), desc=f'Parse plot_data for {fn}'):
            # Get rows by tp
            _tp_df = _df.loc[_df[_time_col] == _tp]
            if not _tp_df.empty:
                _last_row = _tp_df.tail(1).to_numpy()[0]
                _tp += 1
            _new_data.append(_last_row.tolist())
        # Create dataframe with new data
        _pd_df = pd.DataFrame(data=_new_data, columns=_df.columns)
        # Calculate edge per run (EPR)
        if prog_lang.upper() == 'C':
            _pd_df['EPR'] = _pd_df['edges_found'] / _pd_df['total_execs']
        elif prog_lang.upper() == 'JAVA':
            _pd_df['EPR'] = _pd_df['valid_cov'] / _pd_df['# numTrials']
        else:
            raise RuntimeError(f'Unsupported program language {prog_lang}')
        if _sum_df is None:
            _sum_df = _pd_df.copy()
        else:
            _sum_df += _pd_df.copy()
        _pd_cnt += 1
    # print(_sum_df)
    _ave_df = _sum_df.copy() / _pd_cnt
    # Also include ave EPR in sum_df
    _sum_df['ave_EPR'] = _ave_df['EPR']
    return _ave_df, _sum_df


def output_fig(figure: Figure, path: str, tight: bool = True):
    if tight:
        figure.tight_layout()
    figure.savefig(path)
    print('Output to:', path)
    plt.close()
