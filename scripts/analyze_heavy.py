# #!/usr/bin/env python3
# """
# Merge normalized refactoring counts with normalized SpotBugs bug counts per class.
#
# This script reads all refactoring count CSV files from the static directory
#   "normalized_refactoring/"
# and corresponding SpotBugs CSVs from
#   "normalized_spotbugs_output/"
#
# For each refactoring file named:
#   refactoring_vX_to_vY_count.csv
# it will:
#   1) Parse X and Y version numbers.
#   2) Load the refactoring counts (columns: class, qtd_refactorings).
#   3) Load and aggregate SpotBugs bug counts from:
#        normalized_spotbugs_output/normalized_spotbugs_X.csv
#        normalized_spotbugs_output/normalized_spotbugs_Y.csv
#      counting number of bugs per class in each.
#   4) Perform an inner merge across the three datasets on 'class'.
#   5) Save a CSV named:
#        merged_refactorings_spotbugs_X_to_Y.csv
#      containing columns:
#        class,qtd_refactorings,bugs_X,bugs_Y
#
# Usage:
#     python merge_refactorings_spotbugs_counts.py
# """
# import os
# import re
# import pandas as pd
#
# # Static input directories
# REF_DIR = 'normalized_refactoring'
# SB_DIR  = 'normalized_spotbugs_output'
#
# # Pattern to match refactoring count files: refactoring_vX_to_vY_count.csv
# REF_PATTERN = re.compile(r'refactoring_v(?P<v1>[0-9]+(?:\.[0-9]+)*)_to_(?P<v2>[0-9]+(?:\.[0-9]+)*)_count\.csv$')
#
#
# def aggregate_bugs(sb_file):
#     """Load a normalized SpotBugs CSV and return a DataFrame of bug counts per class."""
#     df = pd.read_csv(sb_file)
#     df.columns = df.columns.str.lower()
#     # count rows per class
#     bug_count = df.groupby('class').size().reset_index(name='bug_count')
#     return bug_count
#
#
# def main():
#     # list all refactoring count files
#     try:
#         ref_files = sorted(os.listdir(REF_DIR))
#     except FileNotFoundError:
#         print(f"Directory not found: {REF_DIR}")
#         return
#
#     for fname in ref_files:
#         m = REF_PATTERN.match(fname)
#         if not m:
#             continue
#         v1 = m.group('v1')
#         v2 = m.group('v2')
#         path_ref = os.path.join(REF_DIR, fname)
#         # load refactoring counts
#         df_ref = pd.read_csv(path_ref)
#         df_ref.columns = df_ref.columns.str.lower()
#         # ensure renamed column
#         if 'qtd_refactorings' not in df_ref.columns:
#             df_ref.rename(columns={'qtd.refactorings':'qtd_refactorings'}, inplace=True)
#         # load and aggregate SpotBugs for v1
#         sb1 = os.path.join(SB_DIR, f'normalized_spotbugs_{v1}.csv')
#         if not os.path.exists(sb1):
#             print(f"SpotBugs file not found for {v1}: {sb1}")
#             continue
#         df_sb1 = aggregate_bugs(sb1)
#         df_sb1.rename(columns={'bug_count': f'bugs_{v1}'}, inplace=True)
#         # load and aggregate SpotBugs for v2
#         sb2 = os.path.join(SB_DIR, f'normalized_spotbugs_{v2}.csv')
#         if not os.path.exists(sb2):
#             print(f"SpotBugs file not found for {v2}: {sb2}")
#             continue
#         df_sb2 = aggregate_bugs(sb2)
#         df_sb2.rename(columns={'bug_count': f'bugs_{v2}'}, inplace=True)
#         # inner merge on class
#         df_merge = (
#             df_ref.merge(df_sb1, on='class', how='inner')
#                   .merge(df_sb2, on='class', how='inner')
#         )
#         # select final columns
#         cols = ['class', 'qtd_refactorings', f'bugs_{v1}', f'bugs_{v2}']
#         df_final = df_merge[cols]
#         # save output
#         out_name = f'merged_refactorings_spotbugs_{v1}_to_{v2}.csv'
#         df_final.to_csv(out_name, index=False)
#         print(f'Generated {out_name}')
#
# if __name__ == '__main__':
#     main()

# !/usr/bin/env python3
# """
# Merge normalized refactoring counts with normalized SpotBugs bug counts per class.
#
# Processes CSVs in:
#   <script_dir>/normalized_refactoring/
# and SpotBugs CSVs in:
#   <script_dir>/normalized_spotbugs_output/
#
# For each refactoring file:
#   refactoring_vX_to_vY_count.csv
# it produces:
#   merged_refactorings_spotbugs_X_to_Y.csv
# with columns:
#   class,qtd_refactorings,bugs_X,bugs_Y
# """
import os
import re
import pandas as pd

# Determine base directory (where script resides)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.join(BASE_DIR, 'normalized_refactoring')
SB_DIR  = os.path.join(BASE_DIR, 'normalized_spotbugs_output')

# Regex to match refactoring count files
def ref_pattern():
    return re.compile(r'refactoring_v(?P<v1>[0-9]+(?:\.[0-9]+)*)_to_v?(?P<v2>[0-9]+(?:\.[0-9]+)*)_count\.csv')


def aggregate_bugs(sb_path, bug_col_name):
    df = pd.read_csv(sb_path)
    df.columns = df.columns.str.lower()
    if 'class' not in df.columns:
        raise KeyError(f"Missing 'class' in {sb_path}")
    counts = df.groupby('class').size().reset_index(name=bug_col_name)
    return counts


def main():
    # List refactoring files
    try:
        files = os.listdir(REF_DIR)
    except FileNotFoundError:
        print(f"Refactoring directory not found: {REF_DIR}")
        return

    pattern = ref_pattern()
    for fname in sorted(files):
        m = pattern.match(fname)
        if not m:
            continue
        v1, v2 = m.group('v1'), m.group('v2')
        ref_path = os.path.join(REF_DIR, fname)
        df_ref = pd.read_csv(ref_path)
        df_ref.columns = df_ref.columns.str.lower()
        # unify column name
        if 'qtd.refactorings' in df_ref.columns:
            df_ref.rename(columns={'qtd.refactorings':'qtd_refactorings'}, inplace=True)
        # aggregate bugs for v1
        sb1 = os.path.join(SB_DIR, f'normalized_spotbugs_{v1}.csv')
        if not os.path.exists(sb1):
            print(f"Missing SpotBugs for {v1}: {sb1}")
            continue
        df_sb1 = aggregate_bugs(sb1, f'bugs_{v1}')
        df_sb1.to_csv(f'teste_spot_bug{v1}.csv', index=False)
        # aggregate bugs for v2
        sb2 = os.path.join(SB_DIR, f'normalized_spotbugs_{v2}.csv')
        if not os.path.exists(sb2):
            print(f"Missing SpotBugs for {v2}: {sb2}")
            continue
        df_sb2 = aggregate_bugs(sb2, f'bugs_{v2}')
        df_sb2.to_csv(f'teste_spot_bug{v2}.csv', index=False)

        # merge refactoring counts with bug counts
        df_merge = (
            df_ref[['class','qtd_refactorings']]
            .merge(df_sb1, on='class', how='inner')
            .merge(df_sb2, on='class', how='inner')
        )
        # df_merge = pd.merge(df_sb1, df_sb2, on='class', how='inner')
        out_name = f'merged_refactorings_spotbugs_{v1}_to_{v2}.csv'
        out_path = os.path.join(BASE_DIR, out_name)
        df_merge.to_csv(out_path, index=False)
        print(f'Generated {out_path}')

if __name__ == '__main__':
    main()


