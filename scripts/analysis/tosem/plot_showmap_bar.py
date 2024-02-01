import os
import sys
import json

import pandas as pd
import numpy as np
from numpy import dot
from numpy.linalg import norm

from venn import venn

from common import *

"""
Gather showmap results and depict bars 
"""


def calibrate_into_bar_data(data: dict) -> tuple:
    """
    Calibrate the showmap data to make it suitable for drawing
    bar plots. Specifically, we need to determine all the edge ids
    that are seen by at least one fuzzer and add zeros for fuzzers
    that missed some edges.
    :param data: showmap data for one fuzz target
    :return: data calibrated for plot bars, the number of seen edges
    """
    _calibrate_dict = dict()
    _seen_eids = set()
    for _fuzzer in data:
        # print('one_fuzzer_edges', len(data[_fuzzer].keys()))
        _seen_eids = _seen_eids.union(set(data[_fuzzer].keys()))
    # print('_all_eids', len(_all_eids))
    # Calibrate the data of each fuzzer, i.e., add zeros
    for _fuzzer in data:
        for _eid in _seen_eids:
            if _eid not in data[_fuzzer]:
                data[_fuzzer][_eid] = 0
        # Add values for plot
        _calibrate_dict[_fuzzer] = np.array(list(data[_fuzzer].values()))
    return _calibrate_dict, len(_seen_eids)


def plot_showmap_bar(data: dict, n_edge: int) -> plt.Figure:
    """
    Draw bar plot with showmap data
    :param data: edge coverages grouped by fuzzer
    :param n_edge: number of edges
    """
    plt.clf()
    _width = 0.999 / len(data.keys())
    _multiplier = 0
    # Where each cluster of bars started
    _x = np.arange(n_edge)
    # Canvas
    _fig, _ax = plt.subplots(figsize=(20, 4))
    for _fuzzer, _ecovs in data.items():
        print(_fuzzer)
        # Locate the bar
        _offset = _width * _multiplier
        _multiplier += 1
        # Draw bar
        _rects = _ax.bar(_x + _offset, _ecovs, _width,
                         label=_fuzzer, color=colors[_fuzzer])
    # Set others
    _ax.set_ylabel('Code Coverage')
    _ax.set_xticks([])
    # _ax.legend(loc='upper left', ncols=len(data.keys()))
    # plt.show()
    return _fig


def plot_showmap_bar_one_fuzzer(
        fuzzer_name: str, ecovs: list, n_edge: int, max_y: int) -> plt.Figure:
    """
    Draw using data from one fuzzer
    """
    plt.clf()
    _width = 1
    # Where each cluster of bars started
    _x = np.arange(n_edge)
    # Canvas
    _fig, _ax = plt.subplots(figsize=(8, 4))
    _rects = _ax.bar(_x, ecovs, _width, label=fuzzer_name, color=colors[fuzzer_name])
    # Set others
    _ax.set_ylabel('Code Coverage')
    _ax.set_xticks([])
    _ax.set_ylim(ymin=0, ymax=max_y)
    # _ax.legend(loc='upper left', ncols=len(data.keys()))
    # plt.show()
    return _fig


def merge_showmap_dicts(dicts: list) -> tuple:
    """
    This function provide two types of merges:
    1) Merge by cnt: the resultant edge cov is the counts of coverage
    2) Merge by hit: the resultant edge cov is the number of trials the edge is hit
    :param dicts: a list of dicts containing showmap results
    :return: two dicts produced by the aforementioned two methods of merge
    """
    _cnt_dict = dict()
    _hit_dict = dict()
    for _d in dicts:
        # The keys of a showmap dict are edge ids (eid).
        for _eid in _d:
            if _eid in _cnt_dict:
                _cnt_dict[_eid] += _d[_eid]
                _hit_dict[_eid] += 1
            else:
                _cnt_dict[_eid] = _d[_eid]
                _hit_dict[_eid] = 1
    # Sanitizing
    for _k in _cnt_dict:
        if _k not in _hit_dict:
            raise RuntimeError('Non-equivalent keys in hit and cnt dict!')
    return _cnt_dict, _hit_dict


def draw_bar_plot_and_output(raw_data: dict, fdir: str, tname: str, ftype: str):
    """
    Calibrate data, draw bar plots, and output
    :param raw_data: raw showmap data
    :param fdir: fig dir
    :param tname: the name of the target
    :param ftype: fig type, 'cnt' or 'hit'
    """
    _bar_data, _n_eids = calibrate_into_bar_data(raw_data)
    # Draw bar plots with calibrated data
    _fig = plot_showmap_bar(_bar_data, _n_eids)
    _fpath = os.path.join(fdir, f'bar-{tname}-{ftype}.pdf')
    output_fig(_fig, path=_fpath)


def cal_cosine_dis(v1, v2):
    return 1 - dot(v1, v2)/(norm(v1)*norm(v2))

def cal_cosine_dissim_and_output(raw_data: dict, tname:str, odir: str):
    _bar_data, _n_eids = calibrate_into_bar_data(raw_data)
    _cos_data = dict()
    # Build 2D dict
    for _fuzzer in _bar_data:
        _cos_data[_fuzzer] = dict()
    for _fuzzer1 in _bar_data:
        for _fuzzer2 in _bar_data:
            # If this cos has been calculated, skip it.
            if _fuzzer2 in _cos_data[_fuzzer1]:
                continue
            if _fuzzer1 == _fuzzer2:
                _cos_data[_fuzzer1][_fuzzer2] = float(0)
                _cos_data[_fuzzer2][_fuzzer1] = float(0)
            else:
                _dis = cal_cosine_dis(_bar_data[_fuzzer1], _bar_data[_fuzzer2])
                _cos_data[_fuzzer1][_fuzzer2] = _dis
                _cos_data[_fuzzer2][_fuzzer1] = _dis
    # To csv and store
    _csv_path = os.path.join(odir, f'cosdis-{tname}.csv')
    _df = pd.DataFrame(_cos_data)
    _df.to_csv(_csv_path)
    print('[LOG] Output cosine cosine csv to:', _csv_path)

def determine_maximum_cov_cnts(cal_data: dict):
    _max_cnt = 0
    for _fuzzer in cal_data:
        _max_cnt = max(_max_cnt, cal_data[_fuzzer].max())
    return _max_cnt

def draw_separate_bar_plot_and_output(
        raw_data: dict, fdir: str, tname: str, ftype: str = 'cnt'):
    """
    Calibrate data, draw bar plots, and output
    :param raw_data: raw showmap data
    :param fdir: fig dir
    :param tname: the name of the target
    :param ftype: fig type, 'cnt' or 'hit'
    """
    _bar_data, _n_eids = calibrate_into_bar_data(raw_data)
    _max_y = determine_maximum_cov_cnts(_bar_data)
    for _fuzzer in _bar_data:
        # Draw bar plots with calibrated data
        _fig = plot_showmap_bar_one_fuzzer(_fuzzer, _bar_data[_fuzzer], _n_eids, _max_y)
        _fpath = os.path.join(fdir, f'bar-{tname}-{_fuzzer}-{ftype}.pdf')
        output_fig(_fig, path=_fpath)


def draw_venn_and_output(raw_data: dict, tname: str):
    """
    :param raw_data: dict of times of eids a fuzzer hit, e.g., "afl": {'000':1}
    :param tname: the name of the target
    :return:
    """
    _fig, _ax = plt.subplots(nrows=1, ncols=1, figsize=(5.5, 5.5))
    # Calibrate data into the style suitable for venn
    _venn_dict = dict()
    for _fuzzer in raw_data:
        _venn_dict[_fuzzer] = set(raw_data[_fuzzer].keys())
    # Draw venn
    venn(data=_venn_dict, ax=_ax, legend_loc='best', fontsize=18)
    _fpath = os.path.join(fig_dir, f'venn-{tname}.pdf')
    output_fig(_fig, _fpath)



if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: <this_script> <data_dir> <draw_separate>')
        sys.exit(1)

    # Parse args
    data_dir = os.path.abspath(sys.argv[1])
    draw_separate = bool(int(sys.argv[2]))
    res_dir = os.path.join(data_dir, '_results')
    fig_dir = os.path.join(res_dir, 'fig_showmap')
    if not os.path.exists(fig_dir):
        print('[LOG] Create:', fig_dir)
        os.makedirs(fig_dir)

    # Process each campaign (fuzzer x target)
    cnt_data = dict()
    hit_data = dict()
    for target in targets:
        # Catch data for each fuzzer
        cnt_fuzzer_data = dict()
        hit_fuzzer_data = dict()
        for fuzzer in fuzzers:
            # Locate outs dir
            outs_dir = os.path.join(data_dir, fuzzer, target, 'outs')
            if not os.path.exists(outs_dir):
                # print('[WARN] Do not find:', outs_dir, ', skip...')
                continue
            # Collect showmap results for each trial
            print(f'[LOG] {fuzzer}, {target}')
            camp_dicts = []
            for fn in os.listdir(outs_dir):
                # Skip non out dir
                if not fn.startswith('out-'):
                    continue
                # Locate showmap.json
                sm_json_path = os.path.join(outs_dir, fn, 'default', 'showmap.json')
                with open(sm_json_path, 'r') as f:
                    camp_dicts.append(json.load(f))
            # Merge the results produced by all trials
            cnt_dict, hit_dict = merge_showmap_dicts(camp_dicts)
            # Attach to each fuzzer
            cnt_fuzzer_data[fuzzer] = cnt_dict
            hit_fuzzer_data[fuzzer] = hit_dict
        # Attach to each target (campaign)
        cnt_data[target] = cnt_fuzzer_data
        hit_data[target] = hit_fuzzer_data

    # Calibrate for each target and then draw
    # print('[LOG] Going to calibrate data and draw bar plots.')
    # for target in targets:
    #     print('[LOG] Draw bar plots for target:', target, '...')
    #     if draw_separate:
    #         draw_separate_bar_plot_and_output(cnt_data[target], fig_dir, target)
    #     else:
    #         draw_bar_plot_and_output(cnt_data[target], fig_dir, target, 'cnt')
    #         draw_bar_plot_and_output(hit_data[target], fig_dir, target, 'hit')

    # Calibrate and compute cosine dissimilarities
    print('[LOG] Going to calibrate data and cal cosine distances.')
    for target in targets:
        print('[LOG] Draw cosine distances for target:', target, '...')
        cal_cosine_dissim_and_output(cnt_data[target], target, res_dir)

    # Draw venn diagram
    print('[LOG] Going to draw venn diagrams.')
    for target in targets:
        print('[LOG] Draw venn plots for target:', target, '...')
        try:
            draw_venn_and_output(raw_data=hit_data[target], tname=target)
        except TypeError:
            print('[WARN] Drawing venn failed, please check your data!')

    # Log finish
    print('[LOG] ===========================================')
    print('[LOG] Finish all :-)')
    print('[LOG] ===========================================')
