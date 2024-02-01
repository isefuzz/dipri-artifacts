import sys

from fuzzdata import *

"""
Read in plot_data, average them, and draw fuzz curves.
"""


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print('Usage: python3 draw_fuzz_figs.py <prog_lang> <fuzzdata_dir> <show_legend>')
        exit(0)

    # Directory puts fuzz data
    prog_lang = sys.argv[1]
    fuzzdata_dir = os.path.abspath(sys.argv[2])
    show_legend = bool(int(sys.argv[3]))
    print(f'prog_lang={prog_lang}')
    print(f'fuzzdata_dir={fuzzdata_dir}')
    print(f'show_legend={show_legend}')

    # Parse arguments
    targets = get_targets(prog_lang=prog_lang)
    fuzzers = get_fuzzers(prog_lang=prog_lang)
    res_dir = os.path.join(fuzzdata_dir, '_results')
    fig_dir = os.path.join(res_dir, 'figs')
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)
        os.mkdir(fig_dir)

    # Iterate each out dir
    x_names = ['time', 'execution']
    y_names = ['coverage']
    # y_names = ['coverage', 'crash']
    # Gather all last line into a dataframe
    all_data = []
    index = []
    all_sum_dict = {}
    for target in targets:
        print('===========================================================')
        print('Target:', target)
        df_dict = {}
        for fuzzer in fuzzers:
            print(f'{target}, {fuzzer}')
            outs_dir = os.path.join(fuzzdata_dir, fuzzer, target, 'outs')
            if not os.path.isdir(outs_dir):
                continue
            # Gather average data for subsequent process (drawing pictures, etc.)
            ave_df, sum_df = average_plot_data(prog_lang=prog_lang, outs_dir=outs_dir)
            df_dict[fuzzer] = ave_df
            # Save sum dataframe
            if fuzzer in all_sum_dict:
                if all_sum_dict[fuzzer] is None:
                    all_sum_dict[fuzzer] = sum_df.copy()
                else:
                    all_sum_dict[fuzzer] += sum_df.copy()
            else:
                all_sum_dict[fuzzer] = None
            # Save average dataframe
            csv_path = os.path.join(res_dir, f'{prog_lang}-{target}-{fuzzer}-ave_pd.csv')
            ave_df.to_csv(csv_path)
            print(f'Write average plot_data to `{csv_path}`')
            # Collect last lines
            all_data.append(sum_df.iloc[-1].to_numpy())
            index.append(f'{target}-{fuzzer}')
        if len(df_dict) > 0:
            print('Draw figs...')
            for xn in x_names:
                for yn in y_names:
                    # Draw figures
                    fig = draw_fuzz_plot(prog_lang=prog_lang, df_dict=df_dict,
                                         x_name=xn, y_name=yn, show_legend=show_legend)
                    fig_path = os.path.join(fig_dir, f'{target}-{xn}-{yn}.pdf')
                    output_fig(fig, fig_path)
    # Build df with all last lines
    cols = parse_df_columns(prog_lang) + ['EPR', 'ave_EPR']
    all_df = pd.DataFrame(data=all_data, index=index, columns=cols)
    csv_path = os.path.join(res_dir, f'{prog_lang}-all-fuzzers-pd1.csv')
    all_df.to_csv(csv_path)
    csv_path = os.path.join(res_dir, f'{prog_lang}-all-fuzzers-pd2.csv')
    all_df.T.to_csv(csv_path)
    print(f'Write all fuzzers data to `{csv_path}`')
    # Output total
    total_df = pd.DataFrame(columns=fuzzers, index=['saved_crashes', 'saved_hangs', 'total_execs', 'edges_found'])
    for fuzzer in all_sum_dict:
        total_df[fuzzer] = all_sum_dict[fuzzer].iloc[-1]
    csv_path = os.path.join(res_dir, f'{prog_lang}-total-pd1.csv')
    total_df.to_csv(csv_path)
    csv_path = os.path.join(res_dir, f'{prog_lang}-total-pd2.csv')
    total_df.T.to_csv(csv_path)
    print(f'Write total data to `{csv_path}`')
