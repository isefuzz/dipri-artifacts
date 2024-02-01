import argparse
import os
import pandas as pd
import numpy as np

def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build command line argument parser.
    :return: Arg parser instance.
    """
    _p = argparse.ArgumentParser()
    _p.add_argument('--data_csv', '-d', required=True, type=str,
                    help='Path to data.csv.')
    _p.add_argument('--time_gap', '-g', required=False, type=int, default=900,
                    help='Edge-recording time gap in seconds, default is 900.')
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
    time_gap = args.time_gap
    time_upper = args.time_upper

    # Read in
    data_df = pd.read_csv(data_csv, index_col=0)
    print('Size before fixing:', data_df.size)

    # Iterate and fix
    fixed_data_li = []
    last_tp = -1
    last_row = None
    for row in data_df.to_numpy():
        row_tp = row[-5]
        supposed_tp = last_tp + time_gap
        if (supposed_tp == time_upper) and (row_tp != supposed_tp):
            # Detect a missing of time point
            complemented_row = np.copy(last_row)
            complemented_row[-5] = time_upper
            fixed_data_li.append(complemented_row)
        fixed_data_li.append(row)
        last_tp = row_tp
        last_row = row

    # Write back
    fixed_df = pd.DataFrame(data=fixed_data_li, columns=data_df.columns)
    print('Size after fixing:', fixed_df.size)
    val_cnts = fixed_df['time'].value_counts()
    print(fixed_df['time'].value_counts())
    if val_cnts[time_upper] == val_cnts[time_upper-time_gap]:
        print('Write back fixed_data to:', data_csv)
        fixed_df.to_csv(data_csv)
