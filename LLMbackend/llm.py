import streamlit as st
from LLMbackend.data_extraction import data_extraction
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from config.variable_validation import State
from LLMbackend.agents import agents

class Option_page:
    def __init__(self):
        pass  
        
    def create_resume(self):
        st.subheader('Create-Improve Resume')
        st.write('Help you create or improve existing resume along with JD specific.')

        data_extraction.resume_data_extraction()
        if st.button(label='Next', key = 'LLM_Start'):
            # ----- initialize graph
            if 'work_flow' not in st.session_state:
                st.session_state.work_flow = agents.resume_graph(State)

            # LLM Integration
            user_requirement = st.chat_input('Enter your requirement')

            # ===== START ===== #
            st.session_state.work_flow.invoke({'user_request':user_requirement}, config=st.session_state.config)
            
            if st.button('Next', key='User_requirement'):
                user_suggestion = st.chat_input('Enter either your are satisfied or improvement is required')

                

            


    def create_cv(self):
        pass

