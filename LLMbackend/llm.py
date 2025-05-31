import streamlit as st
from PyPDF2 import PdfReader
import docx
from LLMbackend.data_extraction import data_extraction
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

class Option_page:
    def __init__(self):
        pass

    def create_resume(self):
        st.subheader('Create-Improve Resume')
        st.write('Help you create or improve existing resume along with JD specific.')

        data_extraction.resume_data_extraction()
        if st.button(label='Next', key = 'LLM_Start'):
            # LLM Integration
            user_requirement = st.chat_input('Enter your requirement')
            pass

    def create_cv(self):
        pass