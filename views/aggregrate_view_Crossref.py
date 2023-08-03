import json
import requests
import streamlit as st
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt


def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


@st.cache_data(show_spinner=False)
def count_funders(crossref_funder_counts):
    crossref_funders = load_json(crossref_funder_counts)
    funder_counts = {}
    for funder_id, count_works in crossref_funders.items():
        funder_id = funder_id.replace(
            'http://dx.doi.org/10.13039/', '')
        funder_counts[funder_id] = count_works
    return funder_counts


@st.cache_data(show_spinner=False)
def find_overlap(funders, equivalents):
    funders_ids = set(funders.keys())
    equivalent_ids = set(equivalents.keys())
    return funders_ids & equivalent_ids


@st.cache_data(show_spinner=False)
def display_pie_chart(title, values, labels):
    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    plt.title(title)
    st.pyplot(plt)


@st.cache_data(show_spinner=False)
def calculate_percentages(overlap, funders, equivalents):
    total_funders, overlapping_funders = len(funders), len(overlap)
    overlapping_funders_percentage = (
        overlapping_funders / total_funders) * 100
    non_overlapping_funders_percentage = 100 - overlapping_funders_percentage

    total_assertions = sum(funders.values())
    overlapping_assertions = sum(funders[funder_id] for funder_id in overlap)
    overlapping_assertions_percentage = (
        overlapping_assertions / total_assertions) * 100
    non_overlapping_assertions_percentage = 100 - overlapping_assertions_percentage

    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    mpl.rcParams['font.size'] = 12
    mpl.rcParams['font.weight'] = 'bold'

    axs[0].pie([overlapping_funders_percentage, non_overlapping_funders_percentage], labels=[
        'Overlapping', 'Non-overlapping'], autopct='%1.1f%%')
    axs[0].set_title(f"Overlapping vs Non-overlapping Funder IDs¹\n\n{overlapping_funders} / {total_funders} total funders", fontweight='bold')

    axs[1].pie([overlapping_assertions_percentage, non_overlapping_assertions_percentage], labels=[
        'Overlapping', 'Non-overlapping'], autopct='%1.1f%%')
    axs[1].set_title(f"Overlapping vs Non-overlapping Assertions²\n\n{overlapping_assertions} / {total_assertions} total assertions", fontweight='bold')

    plt.tight_layout()

    st.pyplot(fig)
    st.caption("1. Total number of Funder IDs used in assertions that have been mapped to ROR IDs.\n2. Total number of assertions where the Funder ID is mapped to a ROR ID")


@st.cache_data(show_spinner=False)
def unmapped_to_csv(funders, overlap):
    unmapped_funders = {f'http://dx.doi.org/10.13039/{k}': v for k, v in funders.items() if k not in overlap}
    df = pd.DataFrame(list(unmapped_funders.items()),
                      columns=['Funder ID', 'Count'])
    unmapped_csv = df.to_csv(index=False)
    return unmapped_csv


@st.cache_data(show_spinner=False)
def mapped_to_csv(ror_funder_mapping, overlap):
    unmapped_funders = {f'http://dx.doi.org/10.13039/{k}': v for k, v in ror_funder_mapping.items() if k in overlap}
    df = pd.DataFrame(list(unmapped_funders.items()),
                      columns=['Funder ID', 'ROR ID'])
    mapped_csv = df.to_csv(index=False)
    return mapped_csv


def Crossref_view():
    st.title("Crossref - Aggregrate ROR/Funder Registry Overlap")
    with st.spinner('Generating report...'):
        funders = count_funders('crossref_funders.json')
    if funders:
        equivalents = load_json('ror_funder_registry_mapping.json')
        overlap = find_overlap(funders, equivalents)
        calculate_percentages(overlap, funders, equivalents)
        col1, col2 = st.columns(2)
        unmapped_csv = unmapped_to_csv(funders, overlap)
        col1.download_button(
            label="Download unmapped funders as CSV",
            data=unmapped_csv,
            file_name=f"all_unmapped_funders.csv",
            mime="text/csv",
        )
        mapped_csv = mapped_to_csv(equivalents, overlap)
        col2.download_button(
            label="Download mapped funders as CSV",
            data=mapped_csv,
            file_name=f"all_mapped_funders.csv",
            mime="text/csv",
        )
    else:
        st.write(f"**Error returning Funders from API**")
