import streamlit as st
from load_functions import plot_overlap

@st.cache_data(show_spinner=False, experimental_allow_widgets=True)
def DataCite_view():
    st.title("DataCite - Aggregate ROR/Funder Registry Overlap")
    plot_overlap(st.session_state.datacite_analysis)
    col1, col2 = st.columns(2)
    col1.download_button(
        label="Download unmapped funders as CSV",
        data=open("aggregate_unmapped.csv", "r").read(),
        file_name="aggregate_unmapped.csv.csv",
        mime="text/csv",
    )
    col2.download_button(
        label="Download mapped funders as CSV",
        data=open("aggregate_mapped.csv", "r").read(),
        file_name="aggregate_mapped.csv",
        mime="text/csv",
    )
