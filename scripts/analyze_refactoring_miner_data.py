import json
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import os

def load_commits(full_path):
    with open(full_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and 'commits' in data:
        commits = data['commits']
    elif isinstance(data, list):
        commits = data
    else:
        commits = []

    return [c for c in commits if isinstance(c, dict)]

def count_refactorings(dir_path):
    result = {}
    for fname in sorted(os.listdir(dir_path)):
        if not fname.endswith('.json'):
            continue

        key = fname[:-5]
        full_path = os.path.join(dir_path, fname)
        commits = load_commits(full_path)

        counter = Counter()
        for commit in commits:
            for ref in commit.get('refactorings', []):
                if isinstance(ref, dict):
                    t = ref.get('type', 'Unknown')
                    counter[t] += 1

        total = sum(counter.values())
        print(f"{key}: {len(commits)} commits, {total} refactorings across {len(counter)} types")
        for typ, qtd in counter.most_common():
            print(f"   {typ}: {qtd}")
        if not counter:
            print("   (nenhuma refatoração encontrada)\n")

        result[key] = dict(counter)

    return result

def create_graph(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Convert to DataFrame
    df = pd.DataFrame.from_dict(data, orient='index').fillna(0).astype(int)
    df.index.name = 'version_interval'
    df.index = df.index.str.replace(r'^refactoring_', '', regex=True)

    # 3. Compute total refactorings per interval
    df['total_refactorings'] = df.sum(axis=1)

    # 4. Compute total occurrences per refactoring type across all intervals
    type_totals = df.drop(columns='total_refactorings').sum().sort_values(ascending=False)

    # 5. Plot trends: total refactorings per interval
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['total_refactorings'], marker='o')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Version Interval')
    plt.ylabel('Total de Refatorações')
    plt.title('Total de refatorações por release')
    plt.tight_layout()
    plt.savefig('total_refactorings_trend.png')
    plt.close()

    # 6. Plot top 10 refactoring types
    top10 = type_totals.head(10)
    plt.figure(figsize=(10, 5))
    plt.bar(top10.index, top10.values)
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Refactoring Type')
    plt.ylabel('Total de ocorrências')
    plt.title('Os 10 tipos de refatoração mais frequentes')
    plt.tight_layout()
    plt.savefig('top10_refactoring_types.png')
    plt.close()


if __name__ == '__main__':
    stats = count_refactorings('../refactoring-miner')

    import pprint
    pprint.pprint(stats, sort_dicts=False, width=120)

    file = '../refactoring_counts.json'
    with open(file, 'w', encoding='utf-8') as out:
        json.dump(stats, out, indent=2, ensure_ascii=False)

    create_graph(file)
