import streamlit as st
from services.catalog_service import get_catalog_tree_cached

def render_sidebar(project_id, location):

    st.sidebar.title("Data Discovery")

    if "selected" not in st.session_state:
        st.session_state.selected = None

    tree = get_catalog_tree_cached(project_id, location)

    for lake in tree:
        with st.sidebar.expander(f"🏞️ {lake['name']}", expanded=False):

            for zone in lake["zones"]:
                with st.expander(f"📂 {zone['name']}", expanded=False):

                    for dataset in zone["datasets"]:
                        if st.button(
                            f"📦 {dataset['name']}",
                            key=f"{lake['name']}_{zone['name']}_{dataset['name']}"
                        ):
                            st.session_state.selected = {
                                "lake": lake["name"],
                                "zone": zone["name"],
                                "dataset": dataset["name"],
                                "project": dataset["project"]
                            }