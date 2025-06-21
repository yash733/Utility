from agno.models.ollama import Ollama
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.chroma import ChromaDb
from agno.embedder.ollama import OllamaEmbedder
import streamlit as st

import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_extraction import data_extraction

st.set_page_config(
        page_title="PDF Merger Tool",
        page_icon="📄",
        layout="wide"
    )

st.subheader('Cover Letter')

if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = {}

if 'data' not in st.session_state.data_uploaded:
    st.session_state.data_uploaded['data'] = {}

def input_cv():
    # ----- Input Text | PDF (Meta Data, Resume)
    with st.container():
        st.subheader("1. Input Necessary Information")
        col1, col3, col2 = st.columns([1,0.05,1])

        with col1:
            st.write("Enter Text Information")
            text = st.text_area(label= 'ff', label_visibility='collapsed')
        
        with col3:
            # Create a vertical divider using CSS
            st.markdown("""
            <div style="
                border-left: 2px solid #e0e0e0;
                height: 300px;
                margin: 20px auto;
                position: relative;
            "></div>
            <div style="
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 5px 10px;
                color: #689;
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 15px;
            ">OR</div>
            """, unsafe_allow_html=True)

        with col2:
            st.write("Upload Meta Data (Resume|Personal Description)")

            files = st.file_uploader("Choose PDF file",
                            accept_multiple_files=True,
                            type='pdf',
                            help="Select multiple PDF files to merge")
        
        job_desc = st.text_area(label="Enter Job Description")
        
        if (text or files) and job_desc:
            if st.button(label="Save", key = 'Save1.1'):
                # Upload Text
                if text:
                    st.session_state.data_uploaded['data'].update({'text':text})

                # Upload PDF files
                if files:
                    if 'pdf' not in st.session_state.data_uploaded['data']:
                        st.session_state.data_uploaded['data']['pdf'] = {}

                    for file in files:
                        parsed_data = data_extraction.data_pdf(file)
                        st.session_state.data_uploaded['data']['pdf'].update({file.name : parsed_data})
                
                # Upload Job Description 
                st.session_state.data_uploaded['job_description'] = job_desc
        
        with st.expander(label='Meta Data', expanded=False):
            st.write(st.session_state.data_uploaded)
            # st.write(st.session_state.data_uploaded.get('job_description'))

    if st.button('CLR'):
        st.session_state.data_uploaded = {}

def create_vector_db():
    vector_db = ChromaDb(
        name = "Agno_create_cv",
        embedder = OllamaEmbedder(model = "nomic-embed-text:v1.5")
    )
def agno_():
    agent = Agent(
        model = Ollama(id = "gemma3:12b", provider = "Ollama"),
        knowledge=vector_db
    )


input_cv()