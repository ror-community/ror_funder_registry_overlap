import streamlit as st

def Crossref_view():
    st.title("Crossref - Aggregrate ROR/Funder Registry Overlap")
    st.image("data/crossref_overlap.png", caption="Crossref Overlap Analysis", use_column_width=True)
    st.caption("1. Total number of Funder IDs that have been mapped to ROR IDs.\n2. Total number of assertions where the Funder ID is mapped to a ROR ID")
    col1, col2 = st.columns(2)
    col1.download_button(
        label="Download unmapped funders as CSV",
        data=open("data/aggregate_unmapped.csv", "r").read(),
        file_name="aggregate_unmapped.csv.csv",
        mime="text/csv",
    )
    col2.download_button(
        label="Download mapped funders as CSV",
        data=open("data/aggregate_mapped.csv", "r").read(),
        file_name="aggregate_mapped.csv",
        mime="text/csv",
    )
