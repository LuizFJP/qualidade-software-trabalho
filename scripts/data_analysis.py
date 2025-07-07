"""
Merge CK metrics with Refactoring Miner and SpotBugs outputs.

1) Outputs ck_refactorings_<version>.csv with classes common to CK and Refactoring,
   showing refactoring count and list.
2) Outputs ck_refactorings_spotbugs_<version>.csv adding bug count and types.

Usage:
    python merge_refactor_spotbugs.py --version 5.3
"""
import argparse
import os
import pandas as pd

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--version', required=True, help='Version, e.g. 5.3')
    args = parser.parse_args()
    v = args.version

    path_ck = f'ck_metrics_output/v{v}/ck_metrics.csvclass.csv'
    path_rf = f'normalized_refactoring_output/normalized_refactorings_{v}.csv'
    path_sb = f'normalized_spotbugs_output/normalized_spotbugs_{v}.csv'

    df_ck = pd.read_csv(path_ck)
    df_ck.columns = df_ck.columns.str.lower()

    df_rf = pd.read_csv(path_rf)
    df_rf.columns = df_rf.columns.str.lower()

    df_sb = pd.read_csv(path_sb)
    df_sb.columns = df_sb.columns.str.lower()

    df_rf_agg = (
        df_rf
        .groupby('class')['refactoring_type']
        .agg(refactoring_count='count',
             refactorings=lambda x: ';'.join(sorted(set(x))))
        .reset_index()
    )

    df1 = (
        df_ck[['class']]
        .merge(df_rf_agg, on='class', how='inner')
    )
    out1 = f'ck_refactorings_{v}.csv'
    df1.to_csv(out1, index=False)
    print(f'Wrote: {out1}')

    df_sb_agg = (
        df_sb
        .groupby('class')['bug_type']
        .agg(bug_count='count',
             bug_types=lambda x: ';'.join(sorted(set(x))))
        .reset_index()
    )

    df2 = (
        df1
        .merge(df_sb_agg, on='class', how='inner')
    )
    out2 = f'ck_refactorings_spotbugs_{v}.csv'
    df2.to_csv(out2, index=False)
    print(f'Wrote: {out2}')

if __name__ == '__main__':
    main()
