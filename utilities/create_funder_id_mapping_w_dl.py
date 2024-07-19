import csv
import sys
import json
import requests
import zipfile
import os


def download_and_unzip(record_id, path='.'):
    # Downloading the record from Zenodo
    response = requests.get(f'https://zenodo.org/api/records/{record_id}')
    record = response.json()
    download_link = record['files'][0]['links']['self']
    response = requests.get(download_link, stream=True)
    file_name = download_link.split('/')[-1]
    file_path = os.path.join(path, file_name)
    with open(file_path, 'wb') as out_file:
        for chunk in response.iter_content(chunk_size=1024):
            out_file.write(chunk)
    extracted_file_names = []
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(path)
        extracted_file_names = zip_ref.namelist()
    if extracted_file_names:
        return os.path.splitext(extracted_file_names[0])[0]
    return None


def create_mapping_and_output_json(ror_data_file, json_output_file):
    mapping = {}
    with open(ror_data_file, 'r', encoding="utf8") as f_in:
        ror_data_list = json.load(f_in)
    for ror_data in ror_data_list:
        ror_id = ror_data.get('id', '')
        external_ids = ror_data.get('external_ids', [])
        for external_id in external_ids:
            if external_id.get('type') == 'fundref':
                funder_ids = external_id.get('all', [])
                if external_id.get('preferred'):
                    funder_ids.append(external_id['preferred'])
                funder_ids = list(set(funder_ids))
                for funder_id in funder_ids:
                    mapping[funder_id] = ror_id
    with open(json_output_file, 'w') as json_file:
        json.dump(mapping, json_file)


def delete_files(prefix):
    file_extensions = [".zip", ".json", ".csv"]
    for extension in file_extensions:
        file_path = f"{prefix}{extension}"
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file {file_path}")
        else:
            print(f"The file {file_path} does not exist")


if __name__ == "__main__":
    # Record ID for ROR data dumps
    record_id = input('Record ID for ROR data dump: ')
    prefix = download_and_unzip(record_id)
    json_file_path = f'{prefix}_schema_v2.json'
    if os.path.exists(json_file_path):
        outfile = 'ror_funder_registry_mapping.json'
        create_mapping_and_output_json(json_file_path, outfile)
        delete_files(prefix)
    else:
        print(f"JSON file not found in path: {json_file_path}")
