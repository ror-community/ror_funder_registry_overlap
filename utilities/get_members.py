import requests
import json


def get_response(url, params):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def format_member_records(member_records):
    if 'message' in member_records and 'items' in member_records['message']:
        return {'members': member_records['message']['items']}
    else:
        return None


def save_to_file(member_records, filename):
    with open(filename, 'w') as file:
        json.dump(member_records, file, indent=2)


def main():
    url = 'https://api.labs.crossref.org/members/'
    # Add your email here
    params = {'mailto': 'name@email.com', 'rows': 10000000,
              'select': 'id,primary-title,names'}
    member_records = get_response(url, params)
    if member_records:
        formatted_member_records = format_member_records(member_records)
        if formatted_member_records:
            save_to_file(formatted_member_records, 'members.json')
        else:
            print("Error: No member records found in the API response.")
    else:
        print("Error: Unable to fetch member records from the URL.")


if __name__ == "__main__":
    main()
