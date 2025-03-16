import os
import re
import csv
import json
import time
import argparse
import requests
from functools import wraps


def catch_request_exception(max_retries=3, delay=30):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    retries += 1
                    if retries == max_retries:
                        print(f"All {max_retries} attempts failed.")
                        return 'Error'
                    print(f"Request failed. Retrying in {delay} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(delay)
            return 'Error'
        return wrapper
    return decorator


def read_input_file(input_file):
    funder_ids = []
    with open(input_file, 'r') as file:
        funders = json.load(file)
        for funder in funders['funders']:
            funder_ids.append(funder['id'])
    return funder_ids


def transform_funder_id(funder_id):
    return re.sub('http://dx.doi.org/10.13039/', '*', funder_id)


def form_query_url(funder_id):
    query_url = f"https://api.datacite.org/dois?query=fundingReferences.funderIdentifier:{funder_id}"
    print(f"Query URL: {query_url}")
    return query_url


@catch_request_exception()
def query_datacite_api(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def extract_work_count(response):
    if isinstance(response, str) and response == 'Error':
        return 'Error'
    return response['meta']['total']


def write_output_csv(output_file, data, write_header=False):
    file_exists = os.path.isfile(output_file)
    with open(output_file, 'a') as file:
        writer = csv.writer(file)
        if write_header and not file_exists:
            writer.writerow(['Funder ID', 'Work Count'])
        writer.writerow(data)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Retrieve all work counts for funders in DataCite')
    parser.add_argument(
        '-i', '--input', help='Input JSON file', required=True)
    parser.add_argument(
        '-o', '--output', help='Output CSV file', default='datacite_funder_work_counts.csv')
    return parser.parse_args()


def main():
    args = parse_arguments()
    funder_ids = read_input_file(args.input)
    file_exists = os.path.isfile(args.output)
    if not file_exists:
        write_output_csv(
            args.output, ['Funder ID', 'Work Count'], write_header=True)
    for funder_id in funder_ids:
        transformed_id = transform_funder_id(funder_id)
        url = form_query_url(transformed_id)
        print(f'Retrieving works for {funder_id}...')
        try:
            response = query_datacite_api(url)
            if response != 'Error':
                work_count = extract_work_count(response)
                write_output_csv(args.output, [funder_id, work_count])
                print(f"Successfully retrieved {work_count} works for {funder_id}")
            else:
                print(f"Failed to retrieve works for {funder_id}")
                write_output_csv(args.output, [funder_id, 'Error'])
        except Exception as e:
            print(f"An error occurred while processing {funder_id}: {str(e)}")
            write_output_csv(args.output, [funder_id, 'Error'])


if __name__ == "__main__":
    main()
