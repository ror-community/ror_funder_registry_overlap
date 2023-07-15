import re
import argparse
import csv
import requests
import json

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Retrieve all work counts for funders in DataCite')
    parser.add_argument(
        '-i', '--input', help='Input CSV file', required=True)
    parser.add_argument(
        '-o', '--output', help='Output CSV file', default='datacite_funder_work_counts.csv')
    return parser.parse_args()

def read_input_csv(input_file):
    funder_ids = []
    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            funder_ids.append(row['funder_id'])
    return funder_ids

def transform_funder_id(funder_id):
    return re.sub('http://dx.doi.org/10.13039/','*', funder_id)

def form_query_url(funder_id):
    return f"https://api.datacite.org/dois?query=fundingReferences.funderIdentifier:*{funder_id}"

def query_datacite_api(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def extract_work_count(response):
    return response['meta']['total']

def write_output_csv(output_file, data):
    with open(output_file, 'a') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def main():
    args = parse_arguments()
    funder_ids = read_input_csv(args.input)
    data = []
    for funder_id in funder_ids:
        transformed_id = transform_funder_id(funder_id)
        url = form_query_url(transformed_id)
        print(f'Retrieving works for {funder_id}...')
        response = query_datacite_api(url)
        work_count = extract_work_count(response)
        write_output_csv(args.output, [funder_id, work_count])
    

if __name__ == "__main__":
    main()
