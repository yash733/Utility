import streamlit as st
from LLMbackend.data_extraction import data_extraction
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from config.variable_validation import State
from LLMbackend.agents import agents
from LLMbackend.pdf_creator import save_resume_as_pdf
from LLMbackend.pdf_oprations.merge import main
from logger.logg_rep import logging

# ======================================= #
res_debug = logging.getLogger('create_resume')
res_debug.setLevel(logging.DEBUG)
# ======================================= #

class Option_page:
    def __init__(self):
        pass  
        
    def create_resume(self):
        st.subheader('Create-Improve Resume')
        st.write('Help you create or improve existing resume, wich is JD specific.')
        
        if st.session_state.state == 'START':
            if not st.session_state.get('meta_data_saved'):
                # file upload and processing -->
                with st.spinner('Loading Data'):
                    data_extraction.resume_data_extraction()
                    res_debug.info('Data Extraction Done') # log
                return
            
            # Enter your query, to provide you with the desired resume
            # ----- initialize graph
            if 'work_flow' not in st.session_state:
                # Initialize model and check it worked
                if agents.initialize_model() is None:
                    st.error("Cannot proceed without a valid LLM model")
                    res_debug.error('No Model Instance') # log
                    return
                
                st.session_state.work_flow = agents.resume_graph(State)
                res_debug.info(f'Graph initialized - {st.session_state.work_flow}') # log
                
                chart = st.session_state.work_flow.get_graph().draw_mermaid_png()
                flowchart = './flow_chart.png'
                with open(flowchart, 'wb') as f:
                    f.write(chart)

            # LLM Integration
            user_requirement = st.chat_input('What kind of resume you want to create? Enter your requirement:-')
            res_debug.info(f'User_requirement - {user_requirement}') # log

            if user_requirement: 
                # ===== START ===== #
                with st.spinner('Processing'):
                    st.session_state.work_flow.invoke(input={'user_requirement':user_requirement}, config=st.session_state.config)
                    res_debug.info('First Invoke --') # log
                    res_debug.debug(st.session_state.output_data.get('message_data'))
                    st.rerun()

        elif st.session_state.state == 'Create_Resume':
            res_debug.debug(f'Interrupt Node -{st.session_state.state}') # log

            # After Interrupt -->
            current_state = st.session_state.work_flow.get_state(config = st.session_state.config)
            with st.chat_message('ai'):
                st.markdown(current_state.values['resume'])         

            user_suggestion = st.chat_input('Enter either your are satisfied or improvement is required')
            if user_suggestion:
                with st.spinner('Processing'):
                    st.session_state.work_flow.update_state(config = st.session_state.config, values = {'user_suggestion':user_suggestion})
                    st.session_state.work_flow.invoke(None, config = st.session_state.config)
                    st.rerun()
            else:
                st.stop()           

        elif st.session_state.state == 'Agent': 
            res_debug.debug('Agent Inteface') # log 
            current_state = st.session_state.work_flow.get_state(config = st.session_state.config)
            with st.chat_message('ai'):
                st.markdown(current_state.values['resume'])
            
            with st.expander('Call information'):
                state = st.session_state.work_flow.get_state_history(config = st.session_state.config)
                st.markdown(state)
            
            with st.expander('Chat history'):
                for msg in st.session_state.output_data['message_data']:
                    with st.chat_message(msg.get('role')):
                        st.markdown(msg.get('content'))
            
            # Save .pdf
            save_resume_as_pdf(current_state.values['resume'])                       

    def create_cv(self):
        pass

    def pdf_merge(self):
        main()