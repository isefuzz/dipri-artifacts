import sys
import os
import pandas as pd

"""
fb = fuzzbench
This script is used for merging the data.csv(.gz) produced by fuzzbench.
"""

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Usage: python3 this_script fb_report_dir [exp_filestore]')
        exit(0)

    # The root dir put report dir for each fuzzbench run. The data.csv is typically put
    # under the report_dir
    fb_report_dir = os.path.abspath(sys.argv[1])
    print('fb_report_dir', fb_report_dir)
    # Maybe need to rewrite experiment_filestore
    exp_filestore = None
    if len(sys.argv) > 2:
        exp_filestore = sys.argv[2]
        print('exp_filestore', exp_filestore)

    # Locate all data.csv
    dfs = []
    for fn in os.listdir(fb_report_dir):
        if fn.startswith('.'):
            continue
        report_dir = os.path.join(fb_report_dir, fn)
        if not os.path.isdir(report_dir):
            continue
        # Locate data.csv
        data_csv = os.path.join(report_dir, 'data.csv')
        if not os.path.exists(data_csv):
            # Locate gz and try to gunzip it
            print('[LOG] Do not find data.csv, try to read from data.csv.gz in:', report_dir)
            data_csv_gz = os.path.join(report_dir, 'data.csv.gz')
            if not os.path.exists(data_csv_gz):
                print(f'[WARN] Cannot find data.csv/data.csv.gz in {report_dir}, skip...')
                continue
            print('[LOG] Read from gz:', data_csv_gz)
            dfs.append(pd.read_csv(data_csv_gz))
        else:
            print('[LOG] Find data.csv in:', report_dir)
            dfs.append(pd.read_csv(data_csv))
    # Concat and output
    all_data_csv = os.path.join(fb_report_dir, 'data.csv')
    all_data_df = pd.concat(dfs)
    # Rewrite exp_filestore if given
    if exp_filestore is not None:
        all_data_df['experiment_filestore'] = exp_filestore
        print('[LOG] Change experiment_filestore to:', exp_filestore)
    # Output
    all_data_df.to_csv(all_data_csv)
    print('[LOG] Write all data to:', all_data_csv)
