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
        st.write('Help you create or improve existing resume, wich is JD specific.')
        
        if st.session_state.state == 'START':
            # file upload and processing -->
            with st.spinner('Loading Data'):
                data_extraction.resume_data_extraction()
            
            # Enter your query, to provide you with the desired resume
            if st.button(label='Next', key = 'LLM_Start'):
            # ----- initialize graph
                if 'work_flow' not in st.session_state:
                    st.session_state.work_flow = agents.resume_graph(State)

                # LLM Integration
                user_requirement = st.chat_input('Enter your requirement')

                # ===== START ===== #
                with st.spinner('Processing'):
                    st.session_state.work_flow.invoke({'user_request':user_requirement}, config=st.session_state.config)

        if st.session_state.state == 'Interrupt':
            # After Interrupt -->
            state = st.session_state.work_flow.get_state(config = st.session_state.config)
            st.markdown(state.values.get('resume'))

            user_suggestion = st.chat_input('Enter either your are satisfied or improvement is required')
            if st.button('Next', key='User_requirement'):
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

