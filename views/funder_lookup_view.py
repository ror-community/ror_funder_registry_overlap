import json
import requests
import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def load_funders(funders_file):
    funders = load_json(funders_file)
    return {funder['primary-name']: funder['id'] for funder in funders['funders']}


def get_funder_id(funders, funder_name):
    return funders.get(funder_name)


@st.cache_data(show_spinner=False)
def search_ror(funder_id):
    matched_records = []
    url = 'https://api.ror.org/organizations'
    funder_id = funder_id.replace('http://dx.doi.org/10.13039/', '')
    params = {'query': funder_id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        records = data.get('items', {})
        if records:
            for record in records:
                matched_records.append(
                    {'id': record['id'], 'name': record['name']})
            return matched_records
    return None


def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def funder_lookup_view():
    st.title("Funder Mapping Lookup")
    funders = load_funders('data/funders.json')
    funder_name = st.selectbox('Enter Funder name:', options=[''] + list(funders.keys()))
    submit = st.button("Search")

    if submit:
        if funder_name:
            funder_id = get_funder_id(funders, funder_name)
            with st.spinner('Searching...'):
                ror_records = search_ror(funder_id)
            if ror_records:
                table_data = []
                for record in ror_records:
                    table_data.append({
                        "Funder ID": funder_id,
                        "Funder Name": funder_name,
                        "ROR ID": record['id'],
                        "ROR Name": record['name']
                    })
                df = pd.DataFrame(table_data)
                markdown_table = df.to_markdown(index=False)
                st.markdown(markdown_table, unsafe_allow_html=True)
                st.markdown(f"<div style=\"text-align: right\"><a href=\"https://curation-request.ror.org\">Request correction?</a></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"**No ROR record mapping found for {funder_name} - [Request?](https://curation-request.ror.org)**")



