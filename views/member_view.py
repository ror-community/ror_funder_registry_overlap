import json
import requests
import streamlit as st
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt


@st.cache_data(show_spinner=False)
def load_members(members_file):
    members = load_json(members_file)
    return {member['primary-name']: member['id'] for member in members['members']}


def get_member_id(members, member_name):
    return members.get(member_name)


def count_funders(member_id, rows=1000):
    base_url = 'https://api.crossref.org/members'
    url = f"{base_url}/{member_id}/works"
    funder_counts = {}
    params = {'filter': 'has-funder:true',
              'facet': 'funder-doi:*', 'rows': rows}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        funders = data.get('message', {}).get('facets', {}).get(
            'funder-doi', {}).get('values', None)
        if funders:
            for funder_id, count_works in funders.items():
                funder_id = funder_id.replace(
                    'https://doi.org/10.13039/', '')
                funder_counts[funder_id] = count_works
            return funder_counts
    return None


def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def find_overlap(funders, equivalents):
    funders_ids = set(funders.keys())
    equivalent_ids = set(equivalents.keys())
    return funders_ids & equivalent_ids


def display_pie_chart(title, values, labels):
    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    plt.title(title)
    st.pyplot(plt)


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
    funder_colors = ['tab:blue', 'tab:orange']
    assertion_colors = ['green', 'pink']

    axs[0].pie([overlapping_funders_percentage, non_overlapping_funders_percentage], labels=[
               'Overlapping', 'Non-overlapping'], autopct='%1.1f%%', colors=funder_colors)
    axs[0].set_title(f"Overlapping vs Non-overlapping Funder IDs¹\n\n{format(overlapping_funders, ',d')} / {format(total_funders, ',d')} total funders", fontweight='bold')

    axs[1].pie([overlapping_assertions_percentage, non_overlapping_assertions_percentage], labels=[
               'Overlapping', 'Non-overlapping'], autopct='%1.1f%%', colors=assertion_colors)
    axs[1].set_title(f"Overlapping vs Non-overlapping Assertions²\n\n{format(overlapping_assertions, ',d')} / {format(total_assertions, ',d')} total assertions", fontweight='bold')

    plt.tight_layout()
    return fig


def unmapped_to_csv(funders, overlap):
    unmapped_funders = {f'http://dx.doi.org/10.13039/{k}': v for k, v in funders.items() if k not in overlap}
    df = pd.DataFrame(list(unmapped_funders.items()),
                      columns=['Funder ID', 'Count'])
    unmapped_csv = df.to_csv(index=False)
    return unmapped_csv


def mapped_to_csv(ror_funder_mapping, overlap):
    unmapped_funders = {f'http://dx.doi.org/10.13039/{k}': v for k, v in ror_funder_mapping.items() if k in overlap}
    df = pd.DataFrame(list(unmapped_funders.items()),
                      columns=['Funder ID', 'ROR ID'])
    mapped_csv = df.to_csv(index=False)
    return mapped_csv


def member_view():
    st.title("Crossref Member - ROR/Funder Registry Overlap")
    members = load_members('data/members.json')
    member_name = st.selectbox('Enter Member Name:', options=[
                               ''] + list(members.keys()))
    submit = st.button("Show overlap")

    if member_name and submit:
        if member_name:
            member_id = get_member_id(members, member_name)
        with st.spinner('Checking for funding references...'):
            funders = count_funders(member_id)
        if funders:
            with st.spinner('Generating report...'):
                equivalents = load_json('data/ror_funder_registry_mapping.json')
                overlap = find_overlap(funders, equivalents)
                unmapped_csv = unmapped_to_csv(funders, overlap)
                mapped_csv = mapped_to_csv(equivalents, overlap)
                fig = calculate_percentages(overlap, funders, equivalents)
            st.pyplot(fig)
            st.caption("1. Number of Funder IDs used in member assertions that have been mapped to ROR IDs.\n2. Number of assertions by member where the Funder ID is mapped to a ROR ID")
            col1, col2 = st.columns(2)
            col1.download_button(
                label="Download unmapped funders as CSV",
                data=unmapped_csv,
                file_name=f"member_{member_id}_unmapped_funders.csv",
                mime="text/csv",
            )
            col2.download_button(
                label="Download mapped funders as CSV",
                data=mapped_csv,
                file_name=f"member_{member_id}_mapped_funders.csv",
                mime="text/csv",
            )
        else:
            st.write(f"**No funding references found for {member_name}**")
    elif submit:
        st.write(f"**Please select a member.**")
