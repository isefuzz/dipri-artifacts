import os
import sys
import pandas as pd

from common import targets
from plot_cov_distrib import group_final_cov

if __name__ == '__main__':
    data_csv = os.path.join(sys.argv[1])
    df = pd.read_csv(data_csv)
    grouped_cov = group_final_cov(df)
    std_data = dict()
    for target in grouped_cov:
        target_dict = grouped_cov[target]
        std_target_dict = dict()
        for fuzzer in target_dict:
            std_target_dict[fuzzer] = target_dict[fuzzer].std()
        std_data[target] = std_target_dict
    std_df = pd.DataFrame(std_data, columns=targets)
    # Output to local
    out_dir = os.path.dirname(data_csv)
    std_df.T.to_csv(os.path.join(out_dir, 'final_cov_std.csv'))
