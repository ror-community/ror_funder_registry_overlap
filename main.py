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


def main():
    sidebar_title = st.sidebar.title("Views")

    state = st.session_state
    if 'current_view' not in state:
        state['current_view'] = list(views.keys())[0]
    for view_name in views.keys():
        if st.sidebar.button(view_name):
            state['current_view'] = view_name
    views[state['current_view']]()


if __name__ == '__main__':
    st.set_page_config(initial_sidebar_state="collapsed")
    main()
