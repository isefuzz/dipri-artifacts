import os
import argparse
import pandas as pd

from common import colors, targets, targets_fb, targets_zest

"""
Inspired the ranking method of FuzzBench. This script takes data.csv as 
input and output the (averaged) ranks of the considered fuzzers.
"""


def to_rank_comb(first:float, second: int) -> str:
    # return ('%.2f' % first) + '\\tiny{/' + str(second) + '}'
    return ('%.1f' % first) + '\\tiny{/' + str(second) + '}'


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build command line argument parser.
    :return: Arg parser instance.
    """
    _p = argparse.ArgumentParser()
    _p.add_argument('--data_csv', '-d', required=True, type=str,
                    help='Path to the data.csv file.')
    _p.add_argument('--type', '-t', required=False, type=str, default='rw',
                    help='fb for fuzzbench, rw for realworld')
    _p.add_argument('--output_dir', '-o', required=False, type=str, default='',
                    help='Where to output rank.csv.')
    _p.add_argument('--time_upper', '-u', required=False, type=int, default=82800,
                    help='The upper bound of fuzzing time in seconds, default is 82800 (23hour).')
    return _p


if __name__ == '__main__':

    # Parse command.
    parser = build_arg_parser()
    args = parser.parse_args()
    print(args)

    # Parse args.
    data_csv = os.path.abspath(args.data_csv)
    time_upper = args.time_upper
    output_dir = args.output_dir
    if output_dir == '':
        output_dir = os.path.dirname(data_csv)
    else:
        output_dir = os.path.abspath(output_dir)
    bench_type = args.type
    if bench_type == 'rw':
        targets_of_type = targets
    elif bench_type == 'fb':
        targets_of_type = targets_fb
    elif bench_type == 'zest':
        targets_of_type = targets_zest
    else:
        raise RuntimeError('[ERROR] Unsupported bench_type:', bench_type)

    # Read in data.csv as df
    df = pd.read_csv(data_csv, index_col=0)
    fuzzers = df['fuzzer'].drop_duplicates().to_numpy()
    benchmarks = df['benchmark'].drop_duplicates().to_numpy()

    # Extract the coverage at time uppers.
    data_for_rank = dict()
    last_cov_rows = df[df['time'] == time_upper]
    for bench in benchmarks:
        fuzzer_data = dict()
        for fuzzer in colors:
            if fuzzer not in fuzzers:
                continue
            campaign_cov = last_cov_rows[(last_cov_rows['benchmark'] == bench) &
                                         (last_cov_rows['fuzzer'] == fuzzer)]
            ave_cov = campaign_cov['edges_covered'].mean()
            fuzzer_data[fuzzer] = ave_cov
        data_for_rank[bench] = fuzzer_data

    # Going to rank
    rk_data_df = pd.DataFrame(data_for_rank)
    rank_df = pd.DataFrame(columns=benchmarks, index=fuzzers)
    for bench in benchmarks:
        # Rank for each benchmark
        rank_df[bench] = rk_data_df[bench].rank(ascending=False)
    rank_df['ave_rank'] = rank_df.mean(axis=1)
    print(rank_df)

    # Output
    mean_cov_data = pd.DataFrame(data_for_rank)
    mean_cov_csv = os.path.join(output_dir, 'mean_cov.csv')
    mean_cov_T_csv = os.path.join(output_dir, 'mean_cov_T.csv')
    mean_cov_data.to_csv(mean_cov_csv)
    mean_cov_data.T.to_csv(mean_cov_T_csv)
    print('[LOG] Output to:', mean_cov_csv)
    print('[LOG] Output to:', mean_cov_T_csv)
    rank_csv = os.path.join(output_dir, 'rank.csv')
    rank_T_csv = os.path.join(output_dir, 'rank_T.csv')
    rank_df.to_csv(rank_csv)
    rank_df.T.to_csv(rank_T_csv)
    print('[LOG] Output to:', rank_csv)
    print('[LOG] Output to:', rank_T_csv)

    # Combine and output?
    cov_dict = mean_cov_data.T.to_dict()
    rank_dict = rank_df.T.to_dict()
    comb_dict = dict()
    for fuzzer in cov_dict.keys():
        tmp_dict = dict()
        for target in targets_of_type:
            cov = round(cov_dict[fuzzer][target], 1)
            rank = int(rank_dict[fuzzer][target])
            tmp_dict[target] = to_rank_comb(cov, rank)
        comb_dict[fuzzer] = tmp_dict
    # Also add Ave. Rank
    ave_rank_dict = rank_df['ave_rank'].to_dict()
    rel_rank_dict = rank_df['ave_rank'].rank().to_dict()
    for fuzzer in comb_dict.keys():
        fuzzer_dict = comb_dict[fuzzer]
        abs_ave_rank = round(ave_rank_dict[fuzzer], 2)
        rel_ave_rank = int(rel_rank_dict[fuzzer])
        comb_dict[fuzzer]['ave_rank'] = to_rank_comb(abs_ave_rank, rel_ave_rank)
    print(comb_dict)
    comb_indices = targets_of_type
    comb_indices.append('ave_rank')
    comb_df = pd.DataFrame(comb_dict, index=comb_indices)
    print(comb_df)
    comb_csv = os.path.join(output_dir, 'comb.csv')
    comb_df.to_csv(comb_csv)
    print('[LOG] Output to:', comb_csv)
