import json
import argparse
from bs4 import BeautifulSoup


def convert_records(funder_file):
    funder_records =  {'funders':[]}
    with open(funder_file, 'r+') as f_in:
        funder_rdf = f_in.read()
        soup = BeautifulSoup(funder_rdf , "xml")
        concepts = soup.find_all('skos:Concept')
        for concept in concepts:
            funder_id = concept['rdf:about']
            name = concept.find('skosxl:prefLabel').find(
                'skosxl:Label').find('skosxl:literalForm').text
            aliases = []
            alt_labels = concept.find_all('skosxl:altLabel')
            for alt_label in alt_labels:
                usage_flag = alt_label.find('fref:usageFlag')
                if not usage_flag:
                    label_text = alt_label.find('skosxl:Label').find('skosxl:literalForm').text
                    aliases.append(label_text)
            funder = {"id": funder_id, "primary-name": name, "names": aliases}
            funder_records['funders'].append(funder)
    return funder_records


def save_to_file(funder_records, filename):
    with open(filename, 'w') as file:
        json.dump(funder_records, file, indent=2)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parses Funder RDF into JSON file for ID lookup view")
    parser.add_argument(
        "-i", "--input", help="Input log file path", required=True)
    parser.add_argument(
        "-o", "--output", default='funders.json', help="Output file path", required=False)
    return parser.parse_args()


def main():
    args = parse_arguments()
    funder_records = convert_records(args.input)
    save_to_file(funder_records, args.output)


if __name__ == '__main__':
    main()
