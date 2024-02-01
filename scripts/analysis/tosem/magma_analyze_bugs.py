import sys
import os
import pandas as pd
from matplotlib import pyplot as plt
from venn import venn
from itertools import combinations

"""
Analyze magma-bugs.csv. Make some stats and draw some venns.
"""

n_trial = 10
fuzzers = ['afl', 'aflplusplus', 'aflplusplus_z', 'aflpluzpluz_dipri_ah', 'aflpluzpluz_dipri_vh']
fuzzer_map = {
    'afl': 'afl',
    'aflplusplus': 'aflpp',
    'aflplusplus_z': 'aflpp-Z',
    'aflplusplus_dipri_ah': 'dipri-AH',
    'aflplusplus_dipri_vh': 'dipri-VH',
    'k_scheduler': 'k-scheduler',
}
all_bugs = [
    # libpng (libpng_read_fuzzer), total=7
    'PNG001', 'PNG002', 'PNG003', 'PNG004', 'PNG005',
    'PNG006', 'PNG007',
    # libtiff (tiff_read_rgba_fuzzer, tiffcp), total=14
    'TIF001', 'TIF002', 'TIF003', 'TIF004', 'TIF005',
    'TIF006', 'TIF007', 'TIF008', 'TIF009', 'TIF010',
    'TIF011', 'TIF012', 'TIF013', 'TIF014',
    # libxml2 (xmllint libxml2_xml_read_memory_fuzzer), total=17
    'XML001', 'XML002', 'XML003', 'XML004', 'XML005',
    'XML006', 'XML007', 'XML008', 'XML009', 'XML010',
    'XML011', 'XML012', 'XML013', 'XML014', 'XML015',
    'XML016', 'XML017',
    # sqlite (sqlite3_fuzz), total=20
    'SQL001', 'SQL002', 'SQL003', 'SQL004', 'SQL005',
    'SQL006', 'SQL007', 'SQL008', 'SQL009', 'SQL010',
    'SQL011', 'SQL012', 'SQL013', 'SQL014', 'SQL015',
    'SQL016', 'SQL017', 'SQL018', 'SQL019', 'SQL020',
    # lua (lua), total=4
    'LUA001', 'LUA002', 'LUA003', 'LUA004',
    # libsndfile (sndfile_fuzzer), total=18
    'SND001', 'SND002', 'SND003', 'SND004', 'SND005',
    'SND006', 'SND007', 'SND008', 'SND009', 'SND010',
    'SND011', 'SND012', 'SND013', 'SND014', 'SND015',
    'SND016', 'SND017', 'SND018',
]

def count_total_bugs(bugs: pd.DataFrame) -> pd.DataFrame:
    """
    Count the bugs for statistics.
    """
    _data = []
    for _project in sorted(bugs['project'].drop_duplicates().to_numpy()):
        _proj_data = bugs.loc[bugs['project'] == _project]
        for _target in _proj_data['target'].drop_duplicates():
            _target_data = _proj_data.loc[_proj_data['target'] == _target]
            for _type in bugs['find_type'].drop_duplicates():
                _target_dict = dict(project=_project, target=_target, find_type=_type)
                for _fuzzer in fuzzer_map:
                    _camp_data = _target_data.loc[(_target_data['fuzzer'] == _fuzzer) &
                                                  (_target_data['find_type'] == _type)]
                    _n_total_bug = 0
                    _n_unique_bug = 0
                    _fuzzer_name = fuzzer_map[_fuzzer]
                    if not _camp_data.empty:
                        _n_total_bug = _camp_data['bug'].size
                        _n_unique_bug = _camp_data['bug'].drop_duplicates().size
                    _target_dict[f'{_fuzzer_name}-total'] = _n_total_bug
                    _target_dict[f'{_fuzzer_name}-unique'] = _n_unique_bug
                _data.append(_target_dict)
    return pd.DataFrame(data=_data)

def count_total_bugs2(bugs: pd.DataFrame) -> pd.DataFrame:
    """
    Count the bugs for statistics.
    """
    _data = []
    for _project in sorted(bugs['project'].drop_duplicates().to_numpy()):
        _proj_data = bugs.loc[bugs['project'] == _project]
        for _target in _proj_data['target'].drop_duplicates():
            _target_data = _proj_data.loc[_proj_data['target'] == _target]
            _target_dict = dict(project=_project, target=_target)
            for _fuzzer in fuzzer_map:
                for _type in bugs['find_type'].drop_duplicates():
                    _camp_data = _target_data.loc[(_target_data['fuzzer'] == _fuzzer) &
                                                  (_target_data['find_type'] == _type)]
                    _n_total_bug = 0
                    _n_unique_bug = 0
                    _fuzzer_name = fuzzer_map[_fuzzer]
                    if not _camp_data.empty:
                        _n_total_bug = _camp_data['bug'].size
                        _n_unique_bug = _camp_data['bug'].drop_duplicates().size
                    _target_dict[f'{_fuzzer_name}-{_type}-total'] = _n_total_bug
                    _target_dict[f'{_fuzzer_name}-{_type}-unique'] = _n_unique_bug
            _data.append(_target_dict)
    return pd.DataFrame(data=_data)


def count_total_bugs_by_type(bugs: pd.DataFrame, find_type: str) -> pd.DataFrame:
    """
    Count the bugs for statistics.
    """
    _data = []
    for _project in sorted(bugs['project'].drop_duplicates().to_numpy()):
        _proj_data = bugs.loc[bugs['project'] == _project]
        for _target in _proj_data['target'].drop_duplicates():
            _target_data = _proj_data.loc[_proj_data['target'] == _target]
            _target_dict = dict(project=_project, target=_target)
            for _fuzzer in fuzzer_map:
                if _target == 'libxml2_xml_read_memory_fuzzer' and find_type == 'reached':
                    # This target is problematic, do not distinguish reached and triggered here.
                    _camp_data = _target_data.loc[_target_data['fuzzer'] == _fuzzer]
                else:
                    _camp_data = _target_data.loc[(_target_data['fuzzer'] == _fuzzer) &
                                              (_target_data['find_type'] == find_type)]
                _n_total_bug = 0
                _n_unique_bug = 0
                _fuzzer_name = fuzzer_map[_fuzzer]
                if not _camp_data.empty:
                    _n_total_bug = _camp_data['bug'].size
                    _n_unique_bug = _camp_data['bug'].drop_duplicates().size
                    if _camp_data['bug'].drop_duplicates().size != len(_camp_data['bug'].drop_duplicates()):
                        raise RuntimeError()
                _target_dict[f'{_fuzzer_name}-total'] = _n_total_bug
                _target_dict[f'{_fuzzer_name}-unique'] = _n_unique_bug
            _data.append(_target_dict)
    return pd.DataFrame(data=_data)


def parse_fastest_most_consistent(bugs: pd.DataFrame, find_type: str = 'triggered') -> pd.DataFrame:
    # Put a time for not found
    _not_found_time = 82800 * 2
    # Parse by bugs and fuzzers
    _time_data = dict()
    _trial_data = dict()
    for _bug in bugs['bug'].drop_duplicates():
        _time_data[_bug] = dict()
        _trial_data[_bug] = dict()
        for _fuzzer in fuzzer_map:
            _bug_data = bugs.loc[(bugs['bug'] == _bug) &
                                 (bugs['fuzzer'] == _fuzzer) &
                                 (bugs['find_type'] == find_type)]
            _time2bug = _not_found_time
            _n_buggy_trial = 0
            if not _bug_data.empty:
                _time2bug = _bug_data['time'].mean()
                _n_buggy_trial = _bug_data['trial_id'].drop_duplicates().size
                if _n_buggy_trial > 10:
                    print(_bug_data['find_type'])
                    print(_fuzzer, _bug, _n_buggy_trial, _bug_data['trial_id'].drop_duplicates().to_numpy())
            _time_data[_bug][_fuzzer] = _time2bug
            _trial_data[_bug][_fuzzer] = _n_buggy_trial
    # Count the fastest
    _fastest_times = pd.DataFrame(data=_time_data).min()
    _fastest_count_dict = dict()
    for _fuzzer in fuzzer_map:
        _fastest_count_dict[fuzzer_map[_fuzzer]] = 0
        for _bug in _time_data:
            if _time_data[_bug][_fuzzer] == _fastest_times[_bug]:
                _fastest_count_dict[fuzzer_map[_fuzzer]] += 1
    # Count the most consistent
    _most_trials_df = pd.DataFrame(data=_trial_data).max()
    _consist_count_dict = dict()
    for _fuzzer in fuzzer_map:
        _consist_count_dict[fuzzer_map[_fuzzer]] = 0
        for _bug in _trial_data:
            if _most_trials_df[_bug] != 0 and _trial_data[_bug][_fuzzer] == _most_trials_df[_bug]:
                _consist_count_dict[fuzzer_map[_fuzzer]] += 1
    _fastest_df = pd.DataFrame(data=_fastest_count_dict, index=['fastest'])
    _consist_df = pd.DataFrame(data=_consist_count_dict, index=['most_consistent'])
    return pd.concat([_fastest_df, _consist_df])


def output_csv(odir: str, fn: str, odf: pd.DataFrame):
    _csv = os.path.join(odir, f'{fn}.csv')
    odf.to_csv(_csv)
    print('Output to:', _csv)

def draw_venn_and_output(bugs:pd.DataFrame, odir: str, fn:str, find_type:str, keys: list):
    _bug_dict = dict()
    for _fuzzer in keys:
        _fuzzer_data = bugs.loc[(bugs['fuzzer'] == _fuzzer) &
                                (bugs['find_type'] == find_type)]
        # Also include 'triggered' for 'libxml2_xml_read_memory_fuzzer'
        if find_type == 'reached':
            _t22_data = bugs.loc[(bugs['fuzzer'] == _fuzzer) &
                                 (bugs['target'] == 'libxml2_xml_read_memory_fuzzer') &
                                 (bugs['find_type'] == 'triggered')]
            _fuzzer_data = pd.concat([_fuzzer_data, _t22_data])
        # Targets from the same project may find the same bug, so instead of using
        # the bug columns, we have to concat bug id with target name.
        # _fuzzer_bugs = set(_fuzzer_data['bug'].drop_duplicates())
        _fuzzer_bugs = set()
        for _item in _fuzzer_data[['target', 'bug']].to_numpy():
            _fuzzer_bugs.add(f'{_item[0]}-{_item[1]}')
        _bug_dict[_fuzzer] = _fuzzer_bugs
    # Draw venn
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5.5, 5.5))
    venn(data=_bug_dict, ax=ax, legend_loc='best', fontsize=12)
    # venn(data=_bug_dict, ax=ax, legend_loc='best', fontsize=18)
    # plt.gca().get_legend().remove()
    output_path = os.path.join(odir, f'{fn}.pdf')
    plt.savefig(output_path)
    print('Output to:', output_path)


def parse_venn(bugs:pd.DataFrame, keys: list):
    print('Print venn data for:', keys)
    _bug_dict = dict()
    for _fuzzer in keys:
        _fuzzer_data = bugs.loc[(bugs['fuzzer'] == _fuzzer) &
                                (bugs['find_type'] == 'triggered')]
        # Targets from the same project may find the same bug, so instead of using
        # the bug columns, we have to concat bug id with target name.
        #_fuzzer_bugs = set(_fuzzer_data['bug'].drop_duplicates())
        _fuzzer_bugs = set()
        for _item in _fuzzer_data[['target', 'bug']].to_numpy():
            _fuzzer_bugs.add(f'{_item[0]}-{_item[1]}')
        _bug_dict[_fuzzer] = _fuzzer_bugs
        print(_fuzzer, len(_fuzzer_bugs))
    # Calculate venn data
    # Cal intersection for each comb
    _comb_set = []
    for _comb_size in range(len(keys), 0, -1):
        for _comb in combinations(keys, _comb_size):
            _intersection = None
            for _fuzzer in _comb:
                if _intersection is None:
                    _intersection = _bug_dict[_fuzzer]
                else:
                    _intersection &= _bug_dict[_fuzzer]
            _comb_set.append((set(_comb), _intersection))
    # Cal unique intersection for each comb
    _comb_unique_set = []
    for _idx in range(len(_comb_set)):
        _comb, _interset = _comb_set[_idx]
        _unique_interset = _interset.copy()
        for _idx1 in range(len(_comb_set)):
            if _idx1 == _idx:
                continue
            _comb1, _interset1 = _comb_set[_idx1]
            if _comb.issubset(_comb1):
                # Comb is the subset of comb1
                _unique_interset -= _interset1
        _comb_unique_set.append((_comb, len(_unique_interset), _unique_interset))



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 <this_script> <magma_bugs_csv>')
        exit(0)

    # Parse arg
    magma_bugs_csv = os.path.abspath(sys.argv[1])
    out_dir = os.path.dirname(magma_bugs_csv)

    # Read in csv
    bugs_df = pd.read_csv(magma_bugs_csv)

    # Parse and output to local
    print('total', len(all_bugs))
    output_csv(out_dir, 'total_bug_count', count_total_bugs(bugs_df))
    output_csv(out_dir, 'total_bug_count2', count_total_bugs2(bugs_df))
    output_csv(out_dir, 'total_bug_count_triggered', count_total_bugs_by_type(bugs_df, 'triggered'))
    output_csv(out_dir, 'total_bug_count_reached', count_total_bugs_by_type(bugs_df, 'reached'))
    output_csv(out_dir, 'fastest_consistent_reached', parse_fastest_most_consistent(bugs_df, 'reached'))
    output_csv(out_dir, 'fastest_consistent_triggered', parse_fastest_most_consistent(bugs_df, 'triggered'))

    # Draw venns
    draw_venn_and_output(bugs_df, out_dir, 'venn5-triggered', find_type='triggered',
                         keys=['aflplusplus_dipri_ah', 'aflplusplus_dipri_vh', 'afl', 'aflplusplus', 'aflplusplus_z'])
    draw_venn_and_output(bugs_df, out_dir, 'venn5-reached', find_type='reached',
                         keys=['aflplusplus_dipri_ah', 'aflplusplus_dipri_vh', 'afl', 'aflplusplus', 'aflplusplus_z'])
    draw_venn_and_output(bugs_df, out_dir, 'venn4-triggered', find_type='triggered',
                         keys=['aflplusplus_dipri_ah', 'aflplusplus_dipri_vh', 'afl++', 'k_scheduler'])
    draw_venn_and_output(bugs_df, out_dir, 'venn4-reached', find_type='reached',
                         keys=['aflplusplus_dipri_ah', 'aflplusplus_dipri_vh', 'afl++', 'k_scheduler'])
    draw_venn_and_output(bugs_df, out_dir, 'venn3-triggered', find_type='triggered',
                         keys=['aflplusplus_dipri_ah', 'aflplusplus_dipri_vh', 'k_scheduler'])
    draw_venn_and_output(bugs_df, out_dir, 'venn3-reached', find_type='reached',
                         keys=['aflplusplus_dipri_ah', 'aflplusplus_dipri_vh', 'k_scheduler'])
    # Parse venns
    print('==================================================================')
    parse_venn(bugs_df, keys=['aflplusplus_dipri_ah', 'aflplusplus_dipri_vh', 'afl', 'aflplusplus', 'aflplusplus_z'])
    ah_bugs = bugs_df.loc[(bugs_df['fuzzer'] == 'aflplusplus_dipri_ah') &
                          (bugs_df['find_type'] == 'triggered')]
    print('total', ah_bugs['bug'].drop_duplicates().size)
    for target in ah_bugs['target'].drop_duplicates():
        target_bugs = ah_bugs.loc[ah_bugs['target'] == target]['bug'].drop_duplicates()
        print(target_bugs.size, target)
    print('====================================================================================')
    tiff_bugs1 = set(ah_bugs.loc[ah_bugs['target'] == 'tiff_read_rgba_fuzzer']['bug'].drop_duplicates())
    tiff_bugs2 = set(ah_bugs.loc[ah_bugs['target'] == 'tiffcp']['bug'].drop_duplicates())
    print('tiff_bugs1 & tiff_bugs2', tiff_bugs1 & tiff_bugs2)
    xml_bugs1 = set(ah_bugs.loc[ah_bugs['target'] == 'xmllint']['bug'].drop_duplicates())
    xml_bugs2 = set(ah_bugs.loc[ah_bugs['target'] == 'libxml2_xml_read_memory_fuzzer']['bug'].drop_duplicates())
    print('xml_bugs1 & xml_bugs2', xml_bugs1 & xml_bugs2)
    print('====================================================================================')
    # target = 'libpng_read_fuzzer'
    # target = 'sndfile_fuzzer'
    # target = 'tiff_read_rgba_fuzzer'
    # target = 'tiffcp'
    # target = 'xmllint'
    # target = 'libxml2_xml_read_memory_fuzzer'
    # target = 'lua'
    # target = 'sqlite3_fuzz'
    # fuzzer = 'aflplusplus'
    for fuzzer in bugs_df['fuzzer'].drop_duplicates():
        print('----------------------------------------')
        print('fuzzer:', fuzzer)
        for target in bugs_df['target'].drop_duplicates():
            df = bugs_df.loc[(bugs_df['target'] == target) & (bugs_df['fuzzer'] == fuzzer)]
            rea_df = df.loc[df['find_type'] == 'reached']
            tri_df = df.loc[df['find_type'] == 'triggered']
            rea_set = set(rea_df['bug'].drop_duplicates())
            tri_set = set(tri_df['bug'].drop_duplicates())
            if not tri_set.issubset(rea_set):
                print('target:', target)
                print('rea:', rea_set, 'tri:', tri_set)
                print(rea_set & tri_set, tri_set.issubset(rea_set))
