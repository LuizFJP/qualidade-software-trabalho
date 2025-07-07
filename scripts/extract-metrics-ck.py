import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

def version_key(v):
    parts = list(map(int, v.lstrip('v').split('.')))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)

def main():
    root_dir = '../ck_metrics_output'
    metrics = ['loc', 'wmc', 'dit', 'noc', 'cbo', 'lcom', 'rfc']
    stats_keys = {
        'mean': ('Mean', 'o'),
        'median': ('Median', 's'),
        'var': ('Variance', '^')
    }
    records = []

    releases = sorted(
        [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))],
        key=version_key
    )

    for release in releases:
        path = os.path.join(root_dir, release)
        csvs = glob.glob(os.path.join(path, '*.csv'))
        if not csvs:
            print(f'Aviso: nenhum CSV em {release}')
            continue
        df = pd.read_csv(csvs[0])
        df.columns = df.columns.str.lower()

        if 'type' in df.columns:
            df = df[df['type'].str.lower() == 'class']
        if df.empty:
            continue

        stats = {'release': release}
        for m in metrics:
            print(m)
            stats[f'{m}_mean']   = round(df[m].mean(), 4)
            stats[f'{m}_median'] = round(df[m].median(), 4)
            stats[f'{m}_var']    = round(df[m].var(ddof=0), 4)
        records.append(stats)

        df_stats = pd.DataFrame([stats]).set_index('release')
        df_stats = df_stats.round(4)
        output_path = f'ck_summary_metrics_{release}.csv'
        df_stats.to_csv(output_path)
        print(f'Exportado por versão: {output_path}')

    summary_all = pd.DataFrame(records).set_index('release')
    summary_all = summary_all.sort_index(key=lambda idx: [version_key(v) for v in idx])
    summary_all = summary_all.round(4)

    combined_csv = 'ck_summary_metrics_all_releases.csv'
    summary_all.to_csv(combined_csv)
    print(f'CSV combinado exportado: {combined_csv}')

    for m in metrics:
        for key, (label, marker) in stats_keys.items():
            plt.figure(figsize=(8,4))
            plt.plot(
                summary_all.index,
                summary_all[f'{m}_{key}'],
                marker=marker,
                label=f'{m.upper()} {label}'
            )
            plt.title(f'Evolução de {m.upper()} – {label} Entre Releases')
            plt.xlabel('Release')
            plt.ylabel(label)
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            fn = f'evolution_{m}_{key}_across_20_releases.png'
            plt.savefig(fn)
            plt.close()
            print(f'Gerado: {fn}')

    plt.figure(figsize=(12,6))
    for m in metrics:
        for key, (label, marker) in stats_keys.items():
            plt.plot(
                summary_all.index,
                summary_all[f'{m}_{key}'],
                marker=marker,
                linestyle='-' if key=='mean' else '--' if key=='median' else ':',
                label=f'{m.upper()} {label}'
            )
    plt.title('Evolução de todas as métricas CK – Mean, Median & Variance')
    plt.xlabel('Release')
    plt.ylabel('Valor')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    combined_fn = 'evolution_all_metrics_across_20_releases.png'
    plt.savefig(combined_fn)
    plt.close()
    print(f'Gerado: {combined_fn}')
    mean_cols = [f'{m}_mean' for m in metrics]
    table_df = summary_all[mean_cols]

    fig, ax = plt.subplots(figsize=(len(mean_cols)*1.5 + 2, len(table_df)*0.4 + 2))
    ax.axis('off')
    tbl = ax.table(
        cellText=table_df.values,
        colLabels=[c.replace('_mean','').upper() + ' MEAN' for c in mean_cols],
        rowLabels=table_df.index,
        cellLoc='center',
        loc='center'
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.5)
    plt.tight_layout()
    table_fn = 'ck_metrics_mean_summary_table.png'
    fig.savefig(table_fn, dpi=150)
    plt.close(fig)
    print(f'Gerado tabela de médias: {table_fn}')
if __name__ == '__main__':
    main()
