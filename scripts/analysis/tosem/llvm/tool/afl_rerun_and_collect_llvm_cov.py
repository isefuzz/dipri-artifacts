import os
import sys
import subprocess
import shutil

import pandas as pd

from time import sleep

"""
Rerun afl/afl++-style test inputs against clang instrumented 
targets and extract llvm-cov coverage. 
"""


def run_cmd(args_list: list,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=None):
    print('[LOG]', args_list)
    if stdin is None:
        subprocess.run(args_list, stdout=stdout, stderr=stderr)
    else:
        subprocess.run(args_list, stdin=stdin, stdout=stdout, stderr=stderr)


def extract_input_id(input_name: str) -> str:
    # id:007855,src:007834,time:82752152,execs:92063255,op:havoc,rep:16
    return input_name.split(',')[0].split(':')[1]

def run_each_input_to_gen_raw_profile_data(
        itype: str, tp:str, opts: str, out_dir: str, queue_dir: str, tmp_dir: str):
    # Run each of the test input
    for _fn in sorted(os.listdir(queue_dir)):
        if not _fn.startswith('id'):
            # To avoid none-input files
            continue
        # Locate the test input and extract its id
        _ti_path = os.path.join(queue_dir, _fn)
        _ti_id = extract_input_id(_fn)
        # Build cmd
        _cmd = ['timeout', '2s', tp]
        if opts != '':
            _cmd.extend(opts.split(' '))
        if itype == 'file':
            _cmd.append(_ti_path)
            run_cmd(_cmd)
        elif itype == 'stdin':
            with open(_ti_path, 'r') as _istream:
                run_cmd(_cmd, stdin=_istream)
        else:
            raise RuntimeError('[ERROR] Unsupported input type:', itype)
        # Move the result to tmp dir
        _default_raw_profile_data = os.path.join(out_dir, 'default.profraw')
        # Sanitize
        if not os.path.exists(_default_raw_profile_data):
            raise RuntimeError('[ERROR] Invalid raw profile data:' + _default_raw_profile_data)
        _dest_path = os.path.join(tmp_dir, f'{int(_ti_id)}.profraw')
        run_cmd(['mv', _default_raw_profile_data, _dest_path])


def aggregate_raw_profile_by_time_gaps(
        afltype: str, plot_data: str, tmp_dir: str,
        tupper: int = 82800, tgap: int = 900) -> list:
    _time_points = [_ for _ in range(0, tupper + 1, tgap)]
    # Sanitize
    if not (afltype == 'aflpp' or afltype == 'afl'):
        raise RuntimeError('Unsupported type:', afltype)
    # Read in plot_ata
    _df = pd.read_csv(plot_data, index_col=0, delimiter=', ', engine='python')
    if afltype == 'afl':
        # Adjust df to align with aflpp style
        _df['corpus_count'] = _df['paths_total']
        # Reset index as relative time
        # _new_index = _df.index.to_numpy() - _df.index[0]
        _new_index = _df.index.to_numpy() - (_df.index[-1] - tupper)  # Convenient, but may do not work
        _df = _df.set_index(_new_index)
    # Remove interrupted campaigns
    if (tupper not in _df.index) and (_df.index[-1] < tupper):
        # print(f'time_upper {tupper}, last_idx {_df.index[-1]}')
        # raise RuntimeError('Find a stillborn campaign, please remove: ' + plot_data)
        return []  # Skip
    # Find the largest id at certain time points
    _id_tuples = []
    for _tp in _time_points:
        _col = None
        if _tp == 0:
            # Special case. Use first coverage (or maybe 0) as the coverage at the time point 0.
            _col = _df.iloc[0]
            # _col = pd.Series(dict(edges_found=0, total_execs=0))
        elif _tp in _df.index:
            # Use the row if this tp exists
            _col = _df.loc[_tp]
        else:
            # Find the closest time point
            _tmp = _tp
            while _tmp and _tmp not in _df.index:
                _tmp -= 1
            # Sanitize check!
            if _tmp == 0:
                # raise RuntimeError('Find closest time point failed!: ' + plot_data)
                return []  # Just skip
            _col = _df.loc[_tmp]
        # The largest input id is the number of corpus count -1
        _id_tuples.append((_tp, _col['corpus_count']))
    # Gather *.profraw files and output as profile
    _tp_last = -1
    _tid_max_last = -1
    for _tp, _tid_max in _id_tuples:
        # Locate profile file
        _profile = os.path.join(tmp_dir, f'profile-{str(_tp)}')
        # Locate the list of .profraw files with the _tid_max
        if _tp == 0:
            _relevant_profiles = [os.path.join(tmp_dir, f'{_}.profraw') for _ in range(_tid_max)
                                  if os.path.exists(os.path.join(tmp_dir, f'{_}.profraw'))]
        else:
            _relevant_profiles = [os.path.join(tmp_dir, f'{_}.profraw') for _ in range(_tid_max_last, _tid_max)
                                  if os.path.exists(os.path.join(tmp_dir, f'{_}.profraw'))]
            _profile_last = os.path.join(tmp_dir, f'profile-{str(_tp_last)}')
            _relevant_profiles.append(_profile_last)
        # Run llvm-profdata to get profile data
        _cmd = ['llvm-profdata', 'merge']
        _cmd.extend(_relevant_profiles)
        _cmd.append(f'--output={_profile}')
        run_cmd(_cmd)
        # Mark last tp
        _tp_last = _tp
        _tid_max_last = _tid_max
    # Return time points to prepare for the next step
    return _time_points


def gen_cov_reports(tps: list, tmp_dir: str, bin_paths: list):
    # Extract coverage info coverage report
    for _tp in tps:
        # Locate profile file and the output file
        _profile = os.path.join(tmp_dir, f'profile-{str(_tp)}')
        _output_file = os.path.join(tmp_dir, f'cov-{str(_tp)}')
        # Run llvm-cov report
        _cmd = ['llvm-cov', 'report', '--instr-profile',
                _profile, bin_paths[0]]
        if len(bin_paths) > 1:
            # The rest binaries are objects.
            for _idx in range(1, len(bin_paths)):
                _cmd.append('-object')
                _cmd.append(bin_paths[_idx])
        with open(_output_file, 'w') as _file:
            run_cmd(_cmd, stdout=_file)


def parse_total_branch(total_line: str) -> tuple:
    # The last there values are branch coverage
    _branch_data = [_ for _ in total_line.split(' ') if _ != ''][-3:]
    _branch_total = int(_branch_data[0])
    _branch_miss = int(_branch_data[1])
    _branch_cov = _branch_total - _branch_miss
    _branch_cov = int(_branch_data[0]) - int(_branch_data[1])
    _branch_percent = float(_branch_data[2].rstrip().rstrip('%'))
    return _branch_total, _branch_miss, _branch_cov, _branch_percent

def parse_branch_coverage(tps: list, tmp_dir: str):
    # Parse and extract branch coverage, the last line of llvm-cov report is like:
    # Filename Regions Missed Regions Cover Functions  Missed Functions  Executed Lines Missed Lines Cover Branches Missed Branches Cover
    # TOTAL    62786   60181          4.15% 1544       1441              6.67%    56785 53912        5.06% 40848    38965           4.61%
    _data = []
    for _tp in tps:
        # Locate coverage file
        _cov_file = os.path.join(tmp_dir, f'cov-{str(_tp)}')
        # Read the last line and parse
        with open(_cov_file, 'r') as _f:
            _lines = _f.readlines()
            if len(_lines) == 0:
                continue
            _summary_line = _lines[-1]
        # Sanitizing
        if not _summary_line.startswith('TOTAL'):
            raise RuntimeError('[ERROR] Invalid last line: ' + _cov_file)
        _btotal, _bmiss, _bcov, _bpercent = parse_total_branch(_summary_line)
        # Build dict and append
        _data.append(dict(time=_tp, branch_total=_btotal, branch_miss=_bmiss,
                          branch_cov=_bcov, branch_rate=_bpercent))
    return _data


def main(input_type:str,
         bin_root_dir: str,
         target_bins: str,
         target_opts,
         afl_type,
         afl_out_dir: str):
    # There are may be several bins have coverage data.
    target_bin_paths = [os.path.join(bin_root_dir, _.strip()) for _ in target_bins.split(' ') if _ != '']
    print('[LOG] Target bins:', target_bin_paths)
    sleep(3)
    # Sanitizing
    for bin_path in target_bin_paths:
        if not os.path.exists(bin_path):
            raise RuntimeError('Invalid target BIN: ' + bin_path)
    if not os.path.exists(afl_out_dir):
        raise RuntimeError('Invalid afl out dir: ' + afl_out_dir)
    # Locate dir, prepare tmp and output file
    afl_queue_dir = os.path.join(afl_out_dir, 'queue')
    afl_plot_data = os.path.join(afl_out_dir, 'plot_data')
    llvm_cov_out_csv = os.path.join(afl_out_dir, 'llvm-cov.csv')
    llvm_cov_tmp_dir = os.path.join(afl_out_dir, 'llvm-cov')
    if os.path.exists(llvm_cov_tmp_dir):
        print('[LOG] Recreating:', llvm_cov_tmp_dir)
        shutil.rmtree(llvm_cov_tmp_dir)
    os.mkdir(llvm_cov_tmp_dir)
    # Locate cur_dir
    cur_abspath = os.path.abspath(os.curdir)
    ################################
    # Start to work
    ################################
    # Change into afl_out_dir first
    os.chdir(afl_out_dir)
    # Run each input to generate raw profile data. The executable bin should be placed at the first.
    run_each_input_to_gen_raw_profile_data(
        input_type, target_bin_paths[0], target_opts,
        afl_out_dir, afl_queue_dir, llvm_cov_tmp_dir)
    # Merge raw profdata every 900 seconds
    timepoints = aggregate_raw_profile_by_time_gaps(
        afl_type, afl_plot_data, llvm_cov_tmp_dir)
    # Generate coverage info using llvm-cov report
    gen_cov_reports(timepoints, llvm_cov_tmp_dir, target_bin_paths)
    # Parse coverage file, now we parse branch
    cov_data = parse_branch_coverage(timepoints, llvm_cov_tmp_dir)
    print(cov_data)
    # Preserve to local
    print('[LOG] Output cov_data to:', llvm_cov_out_csv)
    pd.DataFrame(data=cov_data).to_csv(llvm_cov_out_csv)
    # Clear tmp dir
    print('[LOG] Clean llvm-cov dir:', llvm_cov_tmp_dir)
    shutil.rmtree(llvm_cov_tmp_dir)
    # Change back
    os.chdir(cur_abspath)


if __name__ == '__main__':

    if len(sys.argv) != 7:
        print('Usage: <this_script> <input_type> <bin_root_dir> <target_bins> <target_opts> <afl_type> <afl_out_dir>')
        print('Note: <input_type> should be one of \'file\' or \'stdin\'')
        print('Note: <bin_root_dir> is the parent folder preserving coverage binaries')
        print('Note: <target_bins> list of names of the binaries with coverage. The executable bin is put at the first,'
              '\n      i.e., <executable_bin> <object_bin1> <object_bin2>. For example, \'djpeg libjpeg.so\'')
        print('Note: <target_opts> should be quoted in \'\'')
        print('Note: <afl_type> should be one of \'aflpp\' or \'afl\'')
        print('Note: <afl_out_dir> is the parent folder of afl queue/ folder')
        sys.exit(0)

    # Parse and run
    main(input_type=sys.argv[1],
         bin_root_dir=os.path.abspath(sys.argv[2]),
         target_bins=sys.argv[3],
         target_opts=sys.argv[4],
         afl_type=sys.argv[5],
         afl_out_dir=os.path.abspath(sys.argv[6]))

    # Log finish
    print('[LOG] =====================================')
    print('[LOG] Finish all :-)')
    print('[LOG] =====================================')
