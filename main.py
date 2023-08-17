import streamlit as st
from views.member_view import member_view
from views.aggregrate_view_Crossref import Crossref_view
from views.aggregrate_view_Datacite import Datacite_view
from views.funder_lookup_view import funder_lookup_view

views = {
    "Funder Mapping": funder_lookup_view,
    "Crossref - Overlap by member": member_view,
    "Crossref - Aggregrate overlap": Crossref_view,
    "Datacite - Aggregrate overlap": Datacite_view
}

funder_registry_version = '1.51' 
ror_registry_version = '1.29'
works_count_date = '2023/08/03'


def main():
    sidebar_title = st.sidebar.title("Views")

    state = st.session_state
    if 'current_view' not in state:
        state['current_view'] = list(views.keys())[0]
    for view_name in views.keys():
        if st.sidebar.button(view_name):
            state['current_view'] = view_name
    views[state['current_view']]()

    # Add versions and date to the bottom sidebar
    st.sidebar.markdown('---')
    st.sidebar.markdown(f'**Funder Registry version:** {funder_registry_version}')
    st.sidebar.markdown(f'**ROR version:** {ror_registry_version}')
    st.sidebar.markdown(f'**Last refresh date:** {works_count_date}')


if __name__ == '__main__':
    st.set_page_config(initial_sidebar_state="collapsed")
    main()
