import argparse
import json
import csv
import os


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Compare input funder IDs with output CSV to identify missing IDs')
    parser.add_argument(
        '-i', '--input', help='Input JSON file with funder IDs', required=True)
    parser.add_argument(
        '-o', '--output', help='Output CSV file with funder work counts', required=True)
    parser.add_argument(
        '-m', '--missing', help='Output file to write missing IDs', default='missing_funder_ids.json')
    return parser.parse_args()


def read_input_json(input_file):
    """Read input JSON file and extract all funder IDs."""
    try:
        with open(input_file, 'r') as file:
            data = json.load(file)
            funder_ids = [funder['id'] for funder in data['funders']]
            return funder_ids
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return []


def read_output_csv(output_file):
    """Read output CSV file and extract all funder IDs."""
    try:
        output_ids = []
        with open(output_file, 'r') as file:
            reader = csv.reader(file)
            # Skip header if exists
            first_row = next(reader, None)
            if first_row and first_row[0] == 'Funder ID':
                pass  # Header skipped
            else:
                # If first row wasn't a header, it's data
                output_ids.append(first_row[0])
            
            # Process remaining rows
            for row in reader:
                if row and len(row) >= 1:
                    output_ids.append(row[0])
        return output_ids
    except Exception as e:
        print(f"Error reading output file: {str(e)}")
        return []


def find_missing_ids(input_ids, output_ids):
    """Find IDs that are in input but missing from output."""
    # Convert to sets for efficient comparison
    input_set = set(input_ids)
    output_set = set(output_ids)
    
    # Find missing IDs
    missing_ids = input_set - output_set
    
    # Convert back to list for ordered output
    return [id for id in input_ids if id in missing_ids]


def write_missing_ids(missing_ids, output_file, input_file):
    """Write missing IDs to a JSON file with the same structure as input."""
    try:
        # Read original input to maintain structure and additional info
        with open(input_file, 'r') as file:
            original_data = json.load(file)
        
        # Filter funders to only include those with missing IDs
        missing_funders = {
            "funders": [
                funder for funder in original_data["funders"] 
                if funder["id"] in missing_ids
            ]
        }
        
        # Write to output file
        with open(output_file, 'w') as file:
            json.dump(missing_funders, file, indent=2)
        
        return len(missing_funders["funders"])
    except Exception as e:
        print(f"Error writing missing IDs: {str(e)}")
        return 0


def print_summary(total_input, total_output, total_missing):
    """Print summary of comparison results."""
    print("\nCOMPARISON SUMMARY")
    print("-" * 50)
    print(f"Total input IDs:      {total_input}")
    print(f"Total output IDs:     {total_output}")
    print(f"Total missing IDs:    {total_missing}")
    print(f"Missing percentage:   {(total_missing/total_input*100):.2f}%")
    print("-" * 50)


def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Read input and output files
    input_ids = read_input_json(args.input)
    output_ids = read_output_csv(args.output)
    
    # Find missing IDs
    missing_ids = find_missing_ids(input_ids, output_ids)
    
    # Write missing IDs to output file
    missing_count = write_missing_ids(missing_ids, args.missing, args.input)
    
    # Print summary
    print_summary(len(input_ids), len(output_ids), missing_count)
    
    print(f"\nMissing IDs have been saved to {args.missing}")


if __name__ == "__main__":
    main()