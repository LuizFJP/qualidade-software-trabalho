import os
import xml.etree.ElementTree as ET
from collections import Counter
import json
import pandas as pd
import matplotlib.pyplot as plt

def count_bug_categories(dir_path):
    """
    Lê todos os arquivos .xml em dir_path, extrai o atributo `category`
    de cada <BugInstance> e retorna um dict:
      {
        "spotbugs_5.3": {"STYLE": 10, "MALICIOUS_CODE": 25, ...},
        "spotbugs_5.4": { ... },
        ...
      }
    """
    result = {}
    for fname in sorted(os.listdir(dir_path)):
        if not fname.endswith('.xml'):
            continue

        key = os.path.splitext(fname)[0]
        full_path = os.path.join(dir_path, fname)

        tree = ET.parse(full_path)
        root = tree.getroot()

        counter = Counter()
        for bug in root.findall('.//BugInstance'):
            cat = bug.get('category', 'Unknown')
            if cat != "EXPERIMENTAL":
                counter[cat] += 1
            result[key] = dict(counter)

    return result

def generate_table(full_path):
    with open(full_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = 'version'

    # aqui simples sort lexicográfico funciona, mas você pode parsear com packaging.version
    df.index = df.index.str.replace(r'^spotbugs_', '', regex=True)
    df = df.sort_index()

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')
    tbl = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        rowLabels=df.index,
        loc='center'
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.5)

    output_path = '../tabelas-graficos/spotbugs_dataframe.png'
    plt.savefig(output_path, bbox_inches='tight')

def analyze_correctness(full_path):
    with open(full_path, 'r', encoding='utf-8') as f:
        data_graph = json.load(f)

    xml_dir = '../spotbugs'
    for fname in sorted(os.listdir(xml_dir)):
        if not fname.endswith('.xml'):
            continue
        version = os.path.splitext(fname)[0]
        tree = ET.parse(os.path.join(xml_dir, fname))
        root = tree.getroot()
        counts = {}
        for bug in root.findall('.//BugInstance'):
            if bug.get('category') == 'MALICIOUS_CODE':
                bug_type = bug.get('type')
                counts[bug_type] = counts.get(bug_type, 0) + 1
        data_graph[version] = counts

    df = pd.DataFrame.from_dict(data_graph, orient='index').fillna(0).astype(int)
    df.index.name = 'version'
    df.index = df.index.str.replace(r'^spotbugs_', '', regex=True)
    df = df.sort_index()

    ax = df.plot(
        kind='bar',
        stacked=True,
        figsize=(12, 7)
    )
    ax.set_xlabel('SpotBugs Version')
    ax.set_ylabel('Count of Bug Types')
    ax.set_title('Distribuição dos tipos de bugs para a categoria MALICIOUS_CODE ao longo das versões')
    plt.tight_layout()

    output_path = '../tabelas-graficos/correctness_types_distribution.png'
    plt.savefig(output_path, bbox_inches='tight')

if __name__ == '__main__':
    stats = count_bug_categories('../spotbugs')
    import pprint
    pprint.pprint(stats, width=100, sort_dicts=False)

    output_analyze = 'spotbugs_category_counts.json'
    with open(output_analyze, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    generate_table(output_analyze)
    analyze_correctness(output_analyze)


