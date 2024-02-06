import sys
import os

from time import sleep

from afl_rerun_and_collect_llvm_cov import main as rerun

"""
Given a root dir preserving afl outs (i.e., results of multiple trials), 
the path to the target bin, and the opts of the target as well as the way
it reads in inputs, this script automatically locate the out folders and 
rerun the test inputs to get llvm coverage. The rerun logic implemented
using the main function from  `afl_rerun_and_collect_llvm_cov.py` 
"""


def is_afl_out_folder(folder: str) -> bool:
    _fn_list = os.listdir(folder)
    return ('plot_data' in _fn_list) and ('queue' in _fn_list) and \
        (os.path.isdir(os.path.join(folder, 'queue'))) and \
        (not os.path.isdir(os.path.join(folder, 'plot_data')))

def locate_out_folders(root_dir: str) -> list:
    """
    Locate afl out dir recursively. An afl out dir must have a plot_data
    and a queue/ dir under it.
    """
    _out_dirs = set()
    _folder_stack = [root_dir]
    while len(_folder_stack) != 0:
        _dir = _folder_stack.pop()
        if is_afl_out_folder(folder=_dir):
            _out_dirs.add(_dir)
        else:
            # Dig afl out dirs recursively
            for _fn in os.listdir(_dir):
                _path = os.path.join(_dir, _fn)
                if os.path.isdir(_path):
                    _folder_stack.append(_path)
    return sorted(list(_out_dirs))


def determine_afl_type(out_dir: str) -> str:
    """
    Determine afl type ('afl' or 'aflpp') by the header of plot_data
    """
    # Locate plot_data
    _pd_file = os.path.join(out_dir, 'plot_data')
    with open(_pd_file, 'r') as _f:
        _header = _f.readline()
    if _header.startswith('# unix_time'):
        return 'afl'
    elif _header.startswith('# relative_time'):
        return 'aflpp'
    else:
        raise RuntimeError('[ERROR] Unsupported afl-type: ' + out_dir)

def main(outs_root_dir: str,
         bin_root_dir: str,
         target_bins: str,
         target_opts: str,
         input_type: str):
    # Locate all afl out folders
    out_folders = locate_out_folders(root_dir=outs_root_dir)
    afl_type = determine_afl_type(list(out_folders)[0])
    print('[LOG] afl out folders:', out_folders)
    print(f'[LOG] Locate {len(out_folders)} afl out folder(s)...')
    print('[LOG] afl_typle', afl_type)
    sleep(3)
    # Start to rerun for each out dir
    for out_folder in out_folders:
        # Rerun and collect llvm-cov
        rerun(input_type=input_type,
              bin_root_dir=bin_root_dir,
              target_bins=target_bins,
              target_opts=target_opts,
              afl_type=afl_type,
              afl_out_dir=out_folder)


if __name__ == '__main__':

    if len(sys.argv) != 6:
        print('Usage: <this_script> <outs_root_dir> <bin_root_dir> <target_bins> <target_opts> <input_type>')
        print('Note: <outs_root_dir> is the parent folder of afl out folder')
        print('Note: <bin_root_dir> is the parent folder preserving coverage binaries')
        print('Note: <target_bins> list of names of the binaries with coverage. The executable bin is put at the first,'
              '\n      i.e., <executable_bin> <object_bin1> <object_bin2>. For example, \'djpeg libjpeg.so\'')
        print('Note: <target_opts> should be quoted in \'\'')
        print('Note: <afl_type> should be one of \'aflpp\' or \'afl\'')
        print('Note: <input_type> should be one of \'file\' or \'stdin\'')
        sys.exit(0)

    # Parse args and run

    main(outs_root_dir=os.path.abspath(sys.argv[1]),
         bin_root_dir=os.path.abspath(sys.argv[2]),
         target_bins=sys.argv[3],
         target_opts=sys.argv[4],
         input_type=sys.argv[5])

    # Log finish
    print('[LOG] =====================================')
    print('[LOG] Finish all :-)')
    print('[LOG] =====================================')


