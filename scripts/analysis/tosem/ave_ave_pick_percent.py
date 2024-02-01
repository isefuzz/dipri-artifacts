import sys
import os
import numpy as np
import pandas as pd

from common import targets
from extract_pick_percent_data import configs

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: <this_script> <dipri_ave_pick_percent_csv> <out_dir>')
        exit(0)

    # Parse
    dipri_ave_pick_percent_csv = os.path.abspath(sys.argv[1])
    out_dir = os.path.abspath(sys.argv[2])
    df = pd.read_csv(dipri_ave_pick_percent_csv, index_col=0)

    # Preserve N trials
    N = 10
    data_dict = dict()
    for config in configs:
        target_dict = dict()
        for target in targets:
            # Locate data of each campaign
            camp_data = df.loc[(df['fuzzer'] == config) & (df['benchmark'] == target)]
            #print(len(camp_data['trial_id'].to_numpy()))
            # To list and cal average percentage for the first N trials
            ave_ave_pick_percent = 0
            for row in camp_data.to_numpy()[:N]:
                ave_ave_pick_percent += row[-1]
            ave_ave_pick_percent /= N
            target_dict[target] = ave_ave_pick_percent
        data_dict[config] = target_dict
    # Output
    print(data_dict)
    out_csv = os.path.join(out_dir, 'ave-pick-percent.csv')
    pd.DataFrame(data=data_dict).to_csv(out_csv)
