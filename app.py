import streamlit as st
from ui.sidebar import render_sidebar
from ui.main_view import render_main
from config import PROJECT_ID, LOCATION

render_sidebar(PROJECT_ID, LOCATION)

st.set_page_config(layout="wide")
render_main()