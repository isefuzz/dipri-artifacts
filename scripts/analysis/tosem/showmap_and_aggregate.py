import sys
import os
import subprocess
import shutil
import json


"""
Rerun <afl-res>/queue with afl-showmap to collect at each edge.
This script is a prerequisite of the analysis of the distribution
of coverage
"""

args_map = {
    'readpng': [],
    'mjs': ['-f', '@@'],
    'cxxfilt': [],
    'djpeg': ['@@'],
    'mutool': ['draw', '@@', '-o', './out'],
    'nm-new': ['@@'],
    'objdump': ['-d', '@@'],
    'pngtest': ['@@'],
    'readelf': ['-a', '@@'],
    'tcpdump': ['-nr', '@@'],
    'xmllint': ['@@'],
}


def parse_showmap_file_into_dict(path: str) -> dict:
    """
    The content of each showmap file are several "edge_id:cov_cnt" pairs.
    :param path: The path to the showmap file
    :return: the dict recording showmap result
    """
    _dict = dict()
    with open(path, 'r') as _f:
        # Each line is a pair of "edge_id:cov_cnt", e.g., "007769:6"
        for _line in _f.readlines():
            _parts = _line.split(':')
            _edge_id = _parts[0]
            _cov_cnt = int(_parts[1])
            _dict[_edge_id] = _cov_cnt
    return _dict


def aggregate_showmap_dicts(sm_dicts: list) -> dict:
    """
    Aggregate the content of all showmap files into one dict
    """
    _dict = dict()
    for _one_dict in sm_dicts:
        # Aggregate
        for _edge_id in _one_dict.keys():
            if _edge_id in _dict:
                _dict[_edge_id] += _one_dict[_edge_id]
            else:
                _dict[_edge_id] = _one_dict[_edge_id]
    return _dict


def aggregate_showmap_files(dpath: str) -> dict:
    _sm_dicts = [parse_showmap_file_into_dict(os.path.join(dpath, _)) for _ in os.listdir(dpath)]
    return aggregate_showmap_dicts(_sm_dicts)


def output_dict_as_json(jpath: str, data: dict, indent: int = 2):
    with open(jpath, 'w') as _f:
        if indent == 0:
            json.dump(data, _f)
        else:
            json.dump(data, _f, indent=indent)


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print('Usage: <this_script> <showmap_path> <target_path> <fuzzer_dir>')
        sys.exit(1)

    # Parse arges
    showmap_path = os.path.abspath(sys.argv[1])
    target_path = os.path.abspath(sys.argv[2])
    fuzzer_dir = os.path.abspath(sys.argv[3])

    # Determine target_args
    target_name = os.path.basename(target_path)
    target_args = args_map[target_name]

    # Locate camp dir outs dir, specified for this experiment
    camp_dir = os.path.join(fuzzer_dir, target_name)
    outs_dir = os.path.join(camp_dir, 'outs')
    outs_sm_res_json = os.path.join(camp_dir, 'showmap.json')

    # Show
    print('[LOG] showmap_path', showmap_path)
    print('[LOG] target_path', target_path)
    print('[LOG] fuzzer_dir', fuzzer_dir)
    print('[LOG] camp_dir', camp_dir)
    print('[LOG] outs_sm_res_json', outs_sm_res_json)
    print('[LOG] target_name', target_name)
    print('[LOG] target_args', target_args)
    print('[LOG] outs_dir', outs_dir)

    # Repro each out dir with showmap
    out_sm_dicts = []
    for fn in os.listdir(outs_dir):
        if not fn.startswith('out-'):
            continue
        # Locate paths
        out_data_dir = os.path.join(outs_dir, fn, 'default')
        queue_dir = os.path.join(out_data_dir, 'queue')          # Read stored seed cases
        showmap_tmp_dir = os.path.join(out_data_dir, 'showmap_tmp')  # Output showmap results
        agg_sm_res_json = os.path.join(out_data_dir, "showmap.json")
        # Cmd pattern: afl-showmap -i queue_dir -o showmap_tmp_dir -- target_path [target_args]
        print('[LOG] Showmap for:', queue_dir)
        cmd = [showmap_path, '-q', '-i', queue_dir, '-o', showmap_tmp_dir, '--', target_path] + target_args
        # Run showmap
        subprocess.run(cmd)
        print('[LOG] Write showmap results to:', showmap_tmp_dir)
        # Aggregate showmap results into one csv
        agg_sm_res_dict = aggregate_showmap_files(showmap_tmp_dir)
        output_dict_as_json(jpath=agg_sm_res_json, data=agg_sm_res_dict, indent=0)
        print('[LOG] Aggregate and output to:', agg_sm_res_json)
        out_sm_dicts.append(agg_sm_res_dict)
        # Remove tmp dir to save storage
        shutil.rmtree(showmap_tmp_dir)
        print('[LOG] Remove tmp dir:', showmap_tmp_dir)
        print('[LOG] Finish for:', out_data_dir)
        print('[LOG] --------------------------------------------------------')

    # Aggregate the result for each out together
    agg_outs_sm_dict = aggregate_showmap_dicts(out_sm_dicts)
    output_dict_as_json(jpath=outs_sm_res_json, data=agg_outs_sm_dict)
    print('[LOG] Output to:', outs_sm_res_json)
    print('[LOG] Finish ALL :-)')
    print('[LOG] ===========================================================')
