import re
import csv
import json
import time
import argparse
import traceback
import requests


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


@catch_request_exceptions
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


def write_output_csv(output_file, data):
    with open(output_file, 'a') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Retrieve all work counts for funders in Crossref')
    parser.add_argument(
        '-i', '--input', help='Input CSV file', required=True)
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
    data = []
    for funder_id in funder_ids:
        transformed_id = transform_funder_id(funder_id)
        headers = {}
        print(f'Retrieving works for {funder_id}...')
        if args.token:
            headers['Crossref-Plus-API-Token'] = args.token
        if args.user_agent:
            headers['User-Agent'] = args.user_agent
        for i in range(2):  # Retry twice at most
            try:
                response = query_crossref_api(transformed_id, headers)
                work_count = extract_work_count(response)
                write_output_csv(args.output, [funder_id, work_count])
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Retrying after 30 seconds...")
                if i == 0:
                    time.sleep(30)
                else:
                    print("Retry failed. Check the error below and fix it:")
                    traceback.print_exc()
                    break


if __name__ == "__main__":
    main()