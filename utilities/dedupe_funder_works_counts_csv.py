import argparse
import csv


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Deduplicate a CSV file based on the first and second columns.')
    parser.add_argument('-i', '--input', required=True,
                        help='Path to the input CSV file')
    parser.add_argument('-o', '--output', required=True,
                        help='Path to the output deduplicated CSV file')
    return parser.parse_args()


def read_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            data.append(tuple(row))
    return data


def deduplicate_data(data):
    deduplicated_data = {}
    for row in data:
        id_value = row[0]
        numeric_value = int(row[1])
        if id_value in deduplicated_data:
            if numeric_value > deduplicated_data[id_value][1]:
                deduplicated_data[id_value] = (id_value, numeric_value)
        else:
            deduplicated_data[id_value] = (id_value, numeric_value)
    return list(deduplicated_data.values())


def write_csv(file_path, data):
    with open(file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def main():
    args = parse_arguments()
    input_file = args.input
    output_file = args.output

    csv_data = read_csv(input_file)
    deduplicated_data = deduplicate_data(csv_data)
    write_csv(output_file, deduplicated_data)

    print(f'Deduplication complete. Output file: {output_file}')


if __name__ == '__main__':
    main()
