# Merge normalized refactoring counts with normalized SpotBugs bug counts per class.
#
# This script reads all refactoring count CSV files from the static directory
import os
import re
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.join(BASE_DIR, 'normalized_refactoring')
SB_DIR  = os.path.join(BASE_DIR, 'normalized_spotbugs_output')

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
        if 'qtd.refactorings' in df_ref.columns:
            df_ref.rename(columns={'qtd.refactorings':'qtd_refactorings'}, inplace=True)
        sb1 = os.path.join(SB_DIR, f'normalized_spotbugs_{v1}.csv')
        if not os.path.exists(sb1):
            print(f"Missing SpotBugs for {v1}: {sb1}")
            continue
        df_sb1 = aggregate_bugs(sb1, f'bugs_{v1}')
        df_sb1.to_csv(f'teste_spot_bug{v1}.csv', index=False)
        sb2 = os.path.join(SB_DIR, f'normalized_spotbugs_{v2}.csv')
        if not os.path.exists(sb2):
            print(f"Missing SpotBugs for {v2}: {sb2}")
            continue
        df_sb2 = aggregate_bugs(sb2, f'bugs_{v2}')
        df_sb2.to_csv(f'teste_spot_bug{v2}.csv', index=False)

        df_merge = (
            df_ref[['class','qtd_refactorings']]
            .merge(df_sb1, on='class', how='inner')
            .merge(df_sb2, on='class', how='inner')
        )
        out_name = f'merged_refactorings_spotbugs_{v1}_to_{v2}.csv'
        out_path = os.path.join(BASE_DIR, out_name)
        df_merge.to_csv(out_path, index=False)
        print(f'Generated {out_path}')

if __name__ == '__main__':
    main()


