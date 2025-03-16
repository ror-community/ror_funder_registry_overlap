import re
import csv
import json
import time
import argparse
import traceback
import requests
from functools import wraps
import os


def catch_request_exceptions(max_retries=3, delay=30):
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
    return re.sub('http://dx.doi.org/10.13039/', '', funder_id)


@catch_request_exceptions()
def query_crossref_api(funder_id, headers):
    base_url = "https://api.crossref.org/works"
    params = {"filter": f"funder:{funder_id}"}
    if headers:
        response = requests.get(base_url, params=params, headers=headers)
    else:
        response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()


def extract_work_count(response):
    return response['message']['total-results']


def write_output_csv(output_file, data, write_header=False):
    file_exists = os.path.isfile(output_file)

    with open(output_file, 'a') as file:
        writer = csv.writer(file)
        if write_header and not file_exists:
            writer.writerow(['Funder ID', 'Work Count'])
        writer.writerow(data)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Retrieve all work counts for funders in Crossref')
    parser.add_argument(
        '-i', '--input', help='Input JSON file', required=True)
    parser.add_argument(
        '-o', '--output', help='Output CSV file', default='crossref_funder_work_counts.csv')
    parser.add_argument('-t', '--token', type=str, default='',
                        help='Crossref Metadata Plus API token')
    parser.add_argument('-u', '--user_agent', type=str, default='',
                        help='User Agent for the request (mailto:name@email)')
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
        headers = {}
        print(f'Retrieving works for {funder_id}...')

        if args.token:
            headers['Crossref-Plus-API-Token'] = args.token
        if args.user_agent:
            headers['User-Agent'] = args.user_agent

        try:
            response = query_crossref_api(transformed_id, headers)
            if response != 'Error':
                work_count = extract_work_count(response)
                write_output_csv(args.output, [funder_id, work_count])
                print(f"Successfully retrieved {work_count} works for {funder_id}")
            else:
                print(f"Failed to retrieve works for {funder_id}")
        except Exception as e:
            print(f"An error occurred while processing {funder_id}: {str(e)}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
