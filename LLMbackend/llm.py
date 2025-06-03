import streamlit as st
from LLMbackend.data_extraction import data_extraction
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from langchain_community.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from langchain.memory.chat_memory import BaseChatMemory

class Option_page:
    def __init__(self):
        pass
    
    def create_vector_db(self):
        embedding = OllamaEmbeddings(model="nomic-embed-text:v1.5")
        data = list()
        for key, value in st.session_state.data_uploaded['data'].items():
            if isinstance(value, list):
                data.extend(value)
            elif isinstance(value, str):
                data.append(value)

        # vectorstore will hold important data @files
        vectore_store = FAISS.from_texts(texts=data, embedding=embedding)
        retriever = vectore_store.as_retriever()
        #message history 
        #create chain of stuff document chain and retriver chain
        
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