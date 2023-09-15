import sys
import json
import pandas as pd

sys.path.append("..")


def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def count_funders(funder_counts):
    funders = load_json(funder_counts)
    funder_counts = {}
    for funder_id, count_works in funders.items():
        funder_id = funder_id.replace(
            'http://dx.doi.org/10.13039/', '')
        funder_counts[funder_id] = count_works
    return funder_counts


def find_overlap(funders, equivalents):
    funders_ids = set(funders.keys())
    equivalent_ids = set(equivalents.keys())
    return funders_ids & equivalent_ids


def unmapped_to_csv(funders, overlap, filename):
    unmapped_funders = {f'http://dx.doi.org/10.13039/{k}': v for k, v in funders.items() if k not in overlap}
    df = pd.DataFrame(list(unmapped_funders.items()),
                      columns=['Funder ID', 'Count'])
    unmapped_csv = df.to_csv(filename, index=False)
    return unmapped_csv


def mapped_to_csv(ror_funder_mapping, overlap, filename):
    unmapped_funders = {f'http://dx.doi.org/10.13039/{k}': v for k, v in ror_funder_mapping.items() if k in overlap}
    df = pd.DataFrame(list(unmapped_funders.items()),
                      columns=['Funder ID', 'ROR ID'])
    mapped_csv = df.to_csv(filename, index=False)
    return mapped_csv


def create_aggregate_csv():
    equivalents = load_json('ror_funder_registry_mapping.json')
    funders = count_funders(f'crossref_funders.json')
    overlap = find_overlap(funders, equivalents)
    unmapped_filename = f'aggregate_unmapped.csv'
    unmapped_to_csv(funders, overlap, unmapped_filename)
    mapped_filename = f'aggregate_mapped.csv'
    mapped_to_csv(funders, overlap, mapped_filename)

if __name__ == '__main__':
    create_aggregate_csv()


