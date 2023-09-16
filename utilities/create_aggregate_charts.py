import json
import requests
import matplotlib as mpl
import matplotlib.pyplot as plt


def load_json(filename):
	with open(filename, 'r') as file:
		data = json.load(file)
	return data


def count_funders(funder_counts):
	funders = load_json(funder_counts)
	funder_counts = {}
	for funder_id, count_works in funders.items():
		funder_id = funder_id.replace(
			'http://dx.doi.org/10.13039/', '')
		funder_counts[funder_id] = count_works
	return funder_counts


def find_overlap(funders, equivalents):
	funders_ids = set(funders.keys())
	equivalent_ids = set(equivalents.keys())
	return funders_ids & equivalent_ids


def overlap_analysis(overlap, funders, equivalents):
	total_funders, overlapping_funders = len(funders), len(overlap)
	overlapping_funders_percentage = (
		overlapping_funders / total_funders) * 100
	non_overlapping_funders_percentage = 100 - overlapping_funders_percentage

	total_assertions = sum(funders.values())
	overlapping_assertions = sum(funders[funder_id] for funder_id in overlap)
	overlapping_assertions_percentage = (
		overlapping_assertions / total_assertions) * 100
	non_overlapping_assertions_percentage = 100 - overlapping_assertions_percentage
	return {
		'overlapping_funders_percentage': overlapping_funders_percentage,
		'non_overlapping_funders_percentage': non_overlapping_funders_percentage,
		'overlapping_assertions_percentage': overlapping_assertions_percentage,
		'non_overlapping_assertions_percentage': non_overlapping_assertions_percentage,
		'total_funders': total_funders,
		'overlapping_funders': overlapping_funders,
		'total_assertions': total_assertions,
		'overlapping_assertions': overlapping_assertions
	}


def load_crossref():
	funders = count_funders('data/crossref_funders.json')
	equivalents = load_json('data/ror_funder_registry_mapping.json')
	overlap = find_overlap(funders, equivalents)
	analysis = overlap_analysis(overlap, funders, equivalents)
	return analysis


def load_datacite():
	funders = count_funders('data/datacite_funders.json')
	equivalents = load_json('data/ror_funder_registry_mapping.json')
	overlap = find_overlap(funders, equivalents)
	analysis = overlap_analysis(overlap, funders, equivalents)
	return analysis


def save_plot(fig, filename):
    fig.savefig(filename, dpi=300)


def plot_overlap(overlap_data, data_source):
	fig, axs = plt.subplots(1, 2, figsize=(12, 6))
	mpl.rcParams['font.size'] = 12
	mpl.rcParams['font.weight'] = 'bold'

	axs[0].pie(
		[overlap_data['overlapping_funders_percentage'], overlap_data['non_overlapping_funders_percentage']],
		labels=['Overlapping', 'Non-overlapping'],
		autopct='%1.1f%%'
	)
	axs[0].set_title(
		f"Overlapping vs Non-overlapping Funder IDs¹\n\n{format(overlap_data['overlapping_funders'], ',d')} / {format(overlap_data['total_funders'], ',d')} total funders",
		fontweight='bold'
	)

	axs[1].pie(
		[overlap_data['overlapping_assertions_percentage'], overlap_data['non_overlapping_assertions_percentage']],
		labels=['Overlapping', 'Non-overlapping'],
		autopct='%1.1f%%'
	)
	axs[1].set_title(
		f"Overlapping vs Non-overlapping Assertions²\n\n{format(overlap_data['overlapping_assertions'], ',d')} / {format(overlap_data['total_assertions'], ',d')} total assertions",
		fontweight='bold'
	)

	plt.tight_layout()
	filename = f"{data_source}_overlap.png"
	save_plot(fig, filename)


def main():
	crossref_data = load_crossref()
	plot_overlap(crossref_data, "crossref")
	datacite_data = load_datacite()
	plot_overlap(datacite_data, "datacite")

if __name__ == '__main__':
	main()