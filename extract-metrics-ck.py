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
    root_dir = 'ck_metrics_output'
    metrics = ['loc', 'wmc', 'dit', 'noc', 'cbo', 'lcom', 'rfc']
    stats_keys = {
        'mean': ('Mean', 'o'),
        'median': ('Median', 's'),
        'var': ('Variance', '^')
    }
    records = []

    # Ordena pastas de release semanticamente
    releases = sorted(
        [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))],
        key=version_key
    )

    # Processa cada release e coleta estatísticas
    for release in releases:
        path = os.path.join(root_dir, release)
        csvs = glob.glob(os.path.join(path, '*.csv'))
        if not csvs:
            print(f'Aviso: nenhum CSV em {release}')
            continue
        df = pd.read_csv(csvs[0])
        df.columns = df.columns.str.lower()

        # Filtra apenas classes concretas
        if 'type' in df.columns:
            df = df[df['type'].str.lower() == 'class']
        if df.empty:
            continue

        stats = {'release': release}
        for m in metrics:
            stats[f'{m}_mean']   = round(df[m].mean(), 4)
            stats[f'{m}_median'] = round(df[m].median(), 4)
            stats[f'{m}_var']    = round(df[m].var(ddof=0), 4)
        records.append(stats)

        # Exporta CSV por release
        df_stats = pd.DataFrame([stats]).set_index('release')
        df_stats = df_stats.round(4)
        output_path = f'ck_summary_metrics_{release}.csv'
        df_stats.to_csv(output_path)
        print(f'Exportado por versão: {output_path}')

    # Constrói DataFrame de resumo combinado e aplica arredondamento
    summary_all = pd.DataFrame(records).set_index('release')
    summary_all = summary_all.sort_index(key=lambda idx: [version_key(v) for v in idx])
    summary_all = summary_all.round(4)

    # Exporta CSV combinado
    combined_csv = 'ck_summary_metrics_all_releases.csv'
    summary_all.to_csv(combined_csv)
    print(f'CSV combinado exportado: {combined_csv}')

    # 1) PNGs individuais por métrica e estatística
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

    # 2) Gráfico combinado com todas as métricas e estatísticas
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

if __name__ == '__main__':
    main()

