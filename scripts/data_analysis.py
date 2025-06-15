# import pandas as pd
#
# df1 = pd.read_csv('ck_metrics_output/v5.3/ck_metrics.csvclass.csv')
# df2 = pd.read_csv('normalized_refactoring_output/normalized_refactorings_5.3.csv')
# df3 = pd.read_csv('normalized_spotbugs_output/normalized_spotbugs_5.3.csv')
#
# key = 'class'
#
# df1_df2_merged = pd.merge(df1, df2, on=key, how='inner', suffixes=('_ck', '_rf'))
# df1_df2_df3_merged = pd.merge(df1_df2_merged, df3, on=key, how='inner', suffixes=('', '_sb'))
#
# output_path = 'merged_output_5.3_v1.csv'
# df1_df2_df3_merged.to_csv(output_path, columns=['class'], index=False)
# print(f'Merged output saved to {output_path}')

# import pandas as pd
#
# # ---- Ajuste estes caminhos conforme seu ambiente ----
# version = '5.3'
# path_ck = 'ck_metrics_output/v5.3/ck_metrics.csvclass.csv'
# path_sb = 'normalized_spotbugs_output/normalized_spotbugs_5.3.csv'
# path_rf = 'normalized_refactoring_output/normalized_refactorings_5.3.csv'
# output_path = f'merged_output_{version}.csv'
# # -----------------------------------------------------
#
# # 1) Carrega e unifica colunas em lowercase
# df_ck = pd.read_csv(path_ck)
# df_ck.columns = df_ck.columns.str.lower()
#
# df_rf = pd.read_csv(path_rf)
# df_rf.columns = df_rf.columns.str.lower()
#
# df_sb = pd.read_csv(path_sb)
# df_sb.columns = df_sb.columns.str.lower()
#
# # 2) Seleciona só as colunas que vamos usar de cada DF
# #    * ck: métricas CK
# ck_metrics = ['wmc','dit','noc','cbo','lcom','rfc','loc']
# df_ck_sel = df_ck[['class'] + ck_metrics]
#
# #    * refactoring: só tipo de refatoração
# df_rf_sel = df_rf[['class','refactoring_type']]
#
# #    * spotbugs: categoria e tipo de bug
# df_sb_sel = df_sb[['class','category','bug_type']]
#
# # 3) Faz o inner merge em cadeia
# merged = pd.merge(df_ck_sel, df_rf_sel, on='class', how='inner')
# merged = pd.merge(merged, df_sb_sel, on='class', how='inner')
#
# # 4) Salva o resultado final
# merged.to_csv(output_path, index=False)
# print(f'Merged output saved to {output_path}')
#
# # 1) Agrega refatorações: lista única de tipos ou contagem
# df_rf_agg = (
#     df_rf
#     .groupby('class')['refactoring_type']
#     .agg(lambda x: ';'.join(sorted(set(x))))
#     .reset_index()
# )
#
# # 2) Agrega bugs do SpotBugs: lista única de categorias e tipos
# df_sb_agg = (
#     df_sb_sel
#     .groupby('class')
#     .agg({
#         'category': lambda x: ';'.join(sorted(set(x))),
#         'bug_type': lambda x: ';'.join(sorted(set(x)))
#     })
#     .reset_index()
# )
#
# # 3) Agora sim o merge “1:1” em cada classe
# merged = (
#     df_ck_sel
#     .merge(df_rf_agg, on='class', how='inner')
#     .merge(df_sb_agg, on='class', how='inner')
# )
#
# # 4) Salva
# merged.to_csv(f'merged_output_{version}_agg.csv', index=False)
#
#
# import pandas as pd
#
# # ---- Ajuste estes caminhos conforme seu ambiente ----
# version = '5.3'
#
# path_ck = 'ck_metrics_output/v5.3/ck_metrics.csvclass.csv'
# path_sb = 'normalized_spotbugs_output/normalized_spotbugs_5.3.csv'
# path_rf = 'normalized_refactoring_output/normalized_refactorings_5.3.csv'
#
# output_simple = f'merged_output_{version}.csv'
# output_agg   = f'merged_output_{version}_agg.csv'
# # -----------------------------------------------------
#
# # 1) Carrega e normaliza colunas
# df_ck = pd.read_csv(path_ck);  df_ck.columns = df_ck.columns.str.lower()
# df_rf = pd.read_csv(path_rf);  df_rf.columns = df_rf.columns.str.lower()
# df_sb = pd.read_csv(path_sb);  df_sb.columns = df_sb.columns.str.lower()
#
# # 2) Seleciona só as colunas de interesse
# ck_metrics = ['wmc','dit','noc','cbo','lcom','rfc','loc']
# df_ck_sel = df_ck[['class'] + ck_metrics]
# df_rf_sel = df_rf[['class','refactoring_type']]
# df_sb_sel = df_sb[['class','category','bug_type']]
#
# # 3A) Merge simples (vai gerar múltiplas linhas se houver muitos refactorings/bugs)
# merged_simple = (
#     df_ck_sel
#     .merge(df_rf_sel, on='class', how='inner')
#     .merge(df_sb_sel, on='class', how='inner')
# )
# merged_simple.to_csv(output_simple, index=False)
# print(f'Simple merge saved to {output_simple}')
#
# # 3B) Agregação para evitar duplicação (1 linha por classe)
# #    - Refactorings: junta todos os tipos em única célula
# df_rf_agg = (
#     df_rf_sel
#     .groupby('class')['refactoring_type']
#     .agg(lambda s: ';'.join(sorted(set(s))))
#     .reset_index()
# )
#
# #    - Bugs: junta categorias e tipos
# df_sb_agg = (
#     df_sb_sel
#     .groupby('class')
#     .agg({
#         'category':   lambda s: ';'.join(sorted(set(s))),
#         'bug_type':   lambda s: ';'.join(sorted(set(s)))
#     })
#     .reset_index()
# )
#
# # 4) Merge 1:1 com agregados
# merged_agg = (
#     df_ck_sel
#     .merge(df_rf_agg, on='class', how='inner')
#     .merge(df_sb_agg, on='class', how='inner')
# )
# merged_agg.to_csv(output_agg, index=False)
# print(f'Aggregated merge saved to {output_agg}')

#!/usr/bin/env python3
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

    # File paths
    path_ck = f'ck_metrics_output/v{v}/ck_metrics.csvclass.csv'
    path_rf = f'normalized_refactoring_output/normalized_refactorings_{v}.csv'
    path_sb = f'normalized_spotbugs_output/normalized_spotbugs_{v}.csv'

    # Load and lowercase columns
    df_ck = pd.read_csv(path_ck)
    df_ck.columns = df_ck.columns.str.lower()

    df_rf = pd.read_csv(path_rf)
    df_rf.columns = df_rf.columns.str.lower()

    df_sb = pd.read_csv(path_sb)
    df_sb.columns = df_sb.columns.str.lower()

    # Aggregate refactorings per class
    df_rf_agg = (
        df_rf
        .groupby('class')['refactoring_type']
        .agg(refactoring_count='count',
             refactorings=lambda x: ';'.join(sorted(set(x))))
        .reset_index()
    )

    # Merge CK with Refactorings (inner join keeps only common classes)
    df1 = (
        df_ck[['class']]
        .merge(df_rf_agg, on='class', how='inner')
    )
    out1 = f'ck_refactorings_{v}.csv'
    df1.to_csv(out1, index=False)
    print(f'Wrote: {out1}')

    # Aggregate bugs per class
    df_sb_agg = (
        df_sb
        .groupby('class')['bug_type']
        .agg(bug_count='count',
             bug_types=lambda x: ';'.join(sorted(set(x))))
        .reset_index()
    )

    # Merge previous result with SpotBugs aggregation
    df2 = (
        df1
        .merge(df_sb_agg, on='class', how='inner')
    )
    out2 = f'ck_refactorings_spotbugs_{v}.csv'
    df2.to_csv(out2, index=False)
    print(f'Wrote: {out2}')

if __name__ == '__main__':
    main()
