import streamlit as st
from LLMbackend.data_extraction import data_extraction
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from config.variable_validation import State
from LLMbackend.agents import agents
from logger.logg_rep import logging

res_debug = logging.getLogger('create_resume')
res_debug.setLevel(logging.DEBUG)

class Option_page:
    def __init__(self):
        pass  
        
    def create_resume(self):
        st.subheader('Create-Improve Resume')
        st.write('Help you create or improve existing resume, wich is JD specific.')
        
        if st.session_state.state == 'START':
            if not st.session_state.get('data_loaded'):
                # file upload and processing -->
                with st.spinner('Loading Data'):
                    data_extraction.resume_data_extraction()
                    res_debug.info('Data Extraction Done') # log
                    st.session_state['data_loaded'] = True
            
            # Enter your query, to provide you with the desired resume
            # ----- initialize graph
            if 'work_flow' not in st.session_state:
                st.session_state.work_flow = agents.resume_graph(State)
                
                res_debug.info(f'First Run - {st.session_state.work_flow}') # log

                # LLM Integration
                user_requirement = st.chat_input('Enter your requirement')
                if user_requirement: 
                    # ===== START ===== #
                    with st.spinner('Processing'):
                        st.session_state.work_flow.invoke({'user_request':user_requirement}, config=st.session_state.config)

                        res_debug.info('User_requirement') # log

        if st.session_state.state == 'Interrupt':
            # After Interrupt -->
            state = st.session_state.work_flow.get_state(config = st.session_state.config)
            st.markdown(state.values.get('resume'))

            user_suggestion = st.chat_input('Enter either your are satisfied or improvement is required')
            if user_suggestion:
                with st.spinner('Processing'):
                    st.session_state.work_flow.invoke({'user_suggestion':user_suggestion}, config = st.session_state.config)

        if st.session_state.state == 'Agent':
            state = st.session_state.work_flow.get_state(config = st.session_state.config)
            st.markdown(state.values.get('final_resume'))
            
            with st.expander('Call information'):
                state = st.session_state.work_flow.get_state_history(config = st.session_state.config)
                st.markdown(state)
            
            with st.expander('Chat history'):
                for msg in st.session_state.ouput_data['message_data']:
                    with st.chat_message(msg.get('role')):
                        st.markdown(msg.get('content'))

    def create_cv(self):
        pass

