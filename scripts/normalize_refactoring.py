#!/usr/bin/env python3
"""
Batch normalization: count refactoring instances per class in Refactoring Miner JSON outputs.

Processes all JSON files in the static directory 'refactoring-miner' and writes CSVs
with columns `class,qtd_refactorings` into the project root.
"""
import json
import os
from collections import Counter

INPUT_DIR = '../refactoring-miner'
OUTPUT_DIR = '..'  # current directory


def extract_class_from_filepath(fp: str) -> str:
    """Extracts full class name (with .java) from a Refactoring Miner filePath."""
    prefix = 'src/main/java/'
    rel = fp[len(prefix):] if fp.startswith(prefix) else fp
    if rel.endswith('.java'):
        rel = rel[:-5]
    cls = rel.replace('/', '.')
    return cls


def process_json(path: str) -> Counter:
    """Loads a Refactoring Miner JSON and returns a Counter of refactoring instances per class."""
    counts = Counter()
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    for commit in data.get('commits', []):
        for rf in commit.get('refactorings', []):
            # determine unique classes affected by this refactoring instance
            classes = set()
            for loc in rf.get('leftSideLocations', []):
                cls = extract_class_from_filepath(loc.get('filePath', ''))
                classes.add(cls)
            for loc in rf.get('rightSideLocations', []):
                cls = extract_class_from_filepath(loc.get('filePath', ''))
                classes.add(cls)
            # count one per class for this refactoring instance
            for cls in classes:
                counts[cls] += 1
    return counts


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith('.json'))
    if not json_files:
        print(f"No JSON files found in {INPUT_DIR}")
        return

    for fname in json_files:
        path = os.path.join(INPUT_DIR, fname)
        counts = process_json(path)
        base, _ = os.path.splitext(fname)
        csv_name = f'{base}_count.csv'
        csv_path = os.path.join(OUTPUT_DIR, csv_name)
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write('class,qtd_refactorings\n')
            for cls, cnt in counts.most_common():
                f.write(f'{cls},{cnt}\n')
        print(f'Generated {csv_path}')

if __name__ == '__main__':
    main()
