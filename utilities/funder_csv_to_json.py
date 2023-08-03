import csv
import json
import argparse

def to_json(input_file, output_file):
    json_dict = {}
    with open(input_file, 'r+') as f_in:
        reader = csv.reader(f_in)
        for row in reader:
            json_dict[row[0]] = int(row[1])
    with open(output_file, 'w') as f_out:
        json.dump(json_dict, f_out)

def main():
    parser = argparse.ArgumentParser(description='Convert CSV to JSON.')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file path')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output JSON file path')
    args = parser.parse_args()

    to_json(args.input, args.output)

if __name__ == '__main__':
    main()