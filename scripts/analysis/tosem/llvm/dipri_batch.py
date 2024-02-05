import sys
import os

from afl_seek_out_dir_and_rerun import main as seek_and_rerun

"""
Batch scripts specified to DiPri experiments
"""

# A list of targets
fuzzers = [
    # Host fuzzer
    'aflpp', 'aflpp-Z',
    # DiPri config
    'dipri-AE', 'dipri-AH',
    'dipri-PE', 'dipri-PH',
    'dipri-VE', 'dipri-VH',
    # Ablation
    'dipri-cov', 'dipri-len', 'dipri-time',
    'dipri-depth', 'dipri-handicap',
    # Competitors,
    'k-scheduler', 'alphuzz'
]

# Param for each rerun, keys are targets
rerun_params = {
    'cxxfilt': {'bins': 'cxxfilt', 'opts': '', 'intype': 'stdin'},
    'readelf': {'bins': 'readelf', 'opts': '-a', 'intype': 'file'},
    'objdump': {'bins': 'objdump', 'opts': '-d', 'intype': 'file'},
    'nm-new': {'bins': 'nm-new', 'opts': '', 'intype': 'file'},
    'djpeg': {'bins': 'djpeg libjpeg.so', 'opts': '', 'intype': 'file'},
    'mjs': {'bins': 'mjs', 'opts': '-f', 'intype': 'file'},
    'xmllint': {'bins': 'xmllint', 'opts': '', 'intype': 'file'},
    'mutool': {'bins': 'mutool', 'opts': 'draw', 'intype': 'file'},
}


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Usage: <this_script> <data_dir> <llvm_dir> [selected_targets]')
        print('Note: <data_dir> is the folder storing fuzz data.')
        print('Note: <llvm_dir> is the folder storing llvm-cov binaries.')
        exit(0)

    # Parse args
    data_dir = os.path.abspath(sys.argv[1])
    llvm_dir = os.path.abspath(sys.argv[2])
    selected_targets = None
    print('[LOG] data_dir', data_dir)
    print('[LOG] llvm_dir', llvm_dir)
    if len(sys.argv) > 3:
        selected_targets = sys.argv[3].split(' ')
        print('[LOG] selected_targets', selected_targets)
    print('[LOG] =======================================')

    # Start to process
    targets = rerun_params.keys()
    if selected_targets is not None:
        targets = selected_targets
    for target in targets:
        # Locate clang instrumented target dir
        bin_dir = os.path.join(llvm_dir, target)
        # Sanitize
        if not os.path.exists(bin_dir):
            raise RuntimeError('Invalid target dir: ' + bin_dir)
        # Prepare params
        params = rerun_params[target]
        for fuzzer in fuzzers:
            # Check params
            outs_dir = os.path.join(data_dir, fuzzer, target, 'outs')
            if not os.path.exists(outs_dir):
                print('[LOG] Skip as does not find the dir:', outs_dir)
                continue
            # Seek and rerun
            seek_and_rerun(
                outs_root_dir=outs_dir,
                bin_root_dir=bin_dir,
                target_bins=params['bins'],
                target_opts=params['opts'],
                input_type=params['intype']
            )

    # Log finish
    print('[LOG] =====================================')
    print('[LOG] Finish all :-)')
    print('[LOG] =====================================')
