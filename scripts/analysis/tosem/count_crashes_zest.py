import os
import sys
import pandas as pd

zest_fuzzers = ['zest',
                'dipri-AE', 'dipri-AH',
                'dipri-PE', 'dipri-PH',
                'dipri-VE', 'dipri-VH',]

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Usage: <this_script> <data_csv>')
        sys.exit(0)

    # Parse
    data_csv = os.path.abspath(sys.argv[1])
    out_dir = os.path.dirname(data_csv)
    n_trial = 10

    # Read in data and parse
    final_data_li = []
    final_data_li2 = []
    final_data_total = []
    final_data_consist = []
    df = pd.read_csv(data_csv, index_col=0)
    for target in df['target'].drop_duplicates():
        target_data = df.loc[(df['target'] == target)]
        for crash in target_data['crash'].drop_duplicates():
            crash_dict = dict(target=target, crash=crash)
            crash_dict_total = dict(target=target, crash=crash)
            crash_dict_consist = dict(target=target, crash=crash)
            for fuzzer in zest_fuzzers:
                crash_fuzzer_data = df.loc[(df['target'] == target) &
                                           (df['crash'] == crash) &
                                           (df['fuzzer'] == fuzzer)]
                # Make stats
                total_num = 0
                consistency = 0
                if not crash_fuzzer_data.empty:
                    total_num = crash_fuzzer_data['num'].sum()
                    # consistency = crash_fuzzer_data['trial'].drop_duplicates().size / n_trial
                    consistency = crash_fuzzer_data['trail'].drop_duplicates().size / n_trial
                # Add into dict
                crash_dict[f'{fuzzer}-total'] = total_num
                crash_dict[f'{fuzzer}-consistency'] = consistency
                crash_dict_total[fuzzer] = total_num
                crash_dict_consist[fuzzer] = consistency
            final_data_li.append(crash_dict)
            final_data_li2.append(crash_dict_total)
            final_data_li2.append(crash_dict_consist)
            final_data_total.append(crash_dict_total)
            final_data_consist.append(crash_dict_consist)

    # Turn to dataframe
    stats_df = pd.DataFrame(data=final_data_li)
    stats_df.to_csv(os.path.join(out_dir, 'crash_stats.csv'))
    stats_df = pd.DataFrame(data=final_data_li2)
    stats_df.to_csv(os.path.join(out_dir, 'crash_stats2.csv'))
    stats_df = pd.DataFrame(data=final_data_total)
    stats_df.to_csv(os.path.join(out_dir, 'crash_stats_total.csv'))
    stats_df = pd.DataFrame(data=final_data_consist)
    stats_df.to_csv(os.path.join(out_dir, 'crash_stats_consist.csv'))