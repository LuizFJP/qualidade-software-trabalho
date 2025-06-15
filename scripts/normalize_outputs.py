#!/usr/bin/env python3
"""
Normaliza resultados de SpotBugs (XML) e Refactoring Miner (JSON) em CSVs, relacionáveis pelo nome de classe.
Uso:
    python normalize_traccar_results.py --version 5.3
"""
import os
import glob
import argparse
import xml.etree.ElementTree as ET
import json
import pandas as pd


def parse_spotbugs(xml_path):
    """Parse XML SpotBugs e retorna DataFrame com colunas:
    class, bug_type, priority, category, sourcefile, sourcepath, start_line, end_line
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    rows = []
    for bug in root.findall('.//BugInstance'):
        bug_type = bug.get('type')
        priority = bug.get('priority')
        category = bug.get('category')
        cls_elem = bug.find('.//Class')
        cls = cls_elem.get('classname') if cls_elem is not None else None
        sl = bug.find('.//SourceLine')
        if sl is None:
            continue
        sourcefile = sl.get('sourcefile')
        sourcepath = sl.get('sourcepath')
        start = sl.get('start')
        end = sl.get('end')
        rows.append({
            'class': cls,
            'bug_type': bug_type,
            'priority': priority,
            'category': category,
            'sourcefile': sourcefile,
            'sourcepath': sourcepath,
            'start_line': start,
            'end_line': end,
        })
    return pd.DataFrame(rows)


def parse_refactorings(json_paths):
    """Parse JSONs do Refactoring Miner e retorna DataFrame com colunas:
    commit, refactoring_type, description, file_path, class
    """
    rows = []
    for path in json_paths:
        data = json.load(open(path, encoding='utf-8'))
        for commit in data.get('commits', []):
            sha = commit.get('sha1')
            for rf in commit.get('refactorings', []):
                rtype = rf.get('type')
                desc = rf.get('description')
                for loc in rf.get('rightSideLocations', []):
                    fp = loc.get('filePath')
                    # remove prefix up to src/main/java/
                    prefix = 'src/main/java/'
                    if fp.startswith(prefix):
                        cls_path = fp[len(prefix):]
                    else:
                        cls_path = fp
                    # remove extension and convert to dotted
                    if cls_path.endswith('.java'):
                        cls_path = cls_path[:-5]
                    cls = cls_path.replace('/', '.')
                    rows.append({
                        'commit': sha,
                        'refactoring_type': rtype,
                        'description': desc,
                        'file_path': fp,
                        'class': cls,
                    })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--version', required=True, help='versão, ex: 5.3')
    args = parser.parse_args()

    v = args.version
    sb_dir = '../spotbugs'
    sb_path = os.path.join(sb_dir, f'spotbugs_{v}.xml')
    rf_dir = '../refactoring-miner'

    if not os.path.exists(sb_path):
        raise FileNotFoundError(f"SpotBugs XML não encontrado: {sb_path}")

    jsons = [f for f in glob.glob(os.path.join(rf_dir, '*.json')) if f"v{v}" in os.path.basename(f)]
    if not jsons:
        raise FileNotFoundError(f"Nenhum JSON de refatoração encontrado para {v} em {rf_dir}")

    df_sb = parse_spotbugs(sb_path)
    out_sb = f'normalized_spotbugs_{v}.csv'
    df_sb.to_csv(out_sb, index=False)
    print(f'Exportado {out_sb}')

    df_rf = parse_refactorings(jsons)
    out_rf = f'normalized_refactorings_{v}.csv'
    df_rf.to_csv(out_rf, index=False)
    print(f'Exportado {out_rf}')

if __name__ == '__main__':
    main()
