import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from config.config import Config
from sidebar import sidebar, chack_option

st.title("🎯 Personal Utility Tools")

# ----- Session States ----- #
if 'user_selection' not in st.session_state:
    st.session_state.user_selection = {}

if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = {}

if 'ouput_data' not in st.session_state:
    st.session_state.output_data = {}

if 'config' not in st.session_state:
    st.session_state.config = {'configurable':{'thread_id': 'user-1'}}

if 'state' not in st.session_state:
    st.session_state.state = 'START'
# ----- ----- #
if not st.session_state.user_selection.get('llm_model'):
    sidebar()

if st.session_state.user_selection.get('llm_model'):
    #st.rerun()
    chack_option()

