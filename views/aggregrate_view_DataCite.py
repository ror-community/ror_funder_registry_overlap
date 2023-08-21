import streamlit as st
from load_functions import load_json, plot_overlap, unmapped_to_csv, mapped_to_csv

@st.cache_data(show_spinner=False)
def DataCite_view():
    st.title("DataCite - Aggregrate ROR/Funder Registry Overlap")
    plot_overlap(st.session_state.datacite_analysis)
    col1, col2 = st.columns(2)
    unmapped_csv = unmapped_to_csv(
        st.session_state.datacite_funders, st.session_state.datacite_overlap)
    col1.download_button(
        label="Download unmapped funders as CSV",
        data=unmapped_csv,
        file_name=f"all_unmapped_funders.csv",
        mime="text/csv",
    )
    mapped_csv = mapped_to_csv(
        st.session_state.equivalents, st.session_state.datacite_overlap)
    col2.download_button(
        label="Download mapped funders as CSV",
        data=mapped_csv,
        file_name=f"all_mapped_funders.csv",
        mime="text/csv",
    )
