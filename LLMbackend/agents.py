import streamlit as st
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import creacreate_retrieval_chain
from langchain_core.messages.utils import trim_messages
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from data_extraction import data_extraction
from config.resume_template import default
from config.variable_validation import State, response_analysis, expert_review_resume

class agents:
    model = st.session_state.user_selection['llm_model']
    # ======================================== #
    @classmethod
    def history_trimmer(cls, token_size = 500):
        trimmer = trim_messages(
            max_tokens = token_size,
            strategy = 'last',
            token_counter = cls.model,
            start_on = 'system',
            inclue_system = True,
            allow_partial = False
        )
        return trimmer
    
    def create_vector_db(model, prompt):
        embedding = OllamaEmbeddings(model="nomic-embed-text:v1.5")
        
        reduced_document = data_extraction.data_flatning()
        # vectorstore will hold important data @files
        vectore_store = FAISS.from_documents(documents=reduced_document, embedding=embedding)
        retriever = vectore_store.as_retriever()

        doc_chain = create_stuff_documents_chain(model, prompt)
        relevant_info = creacreate_retrieval_chain(doc_chain, retriever)
        return relevant_info
    # ========================================= #

    @classmethod
    def create_resume(cls, state: State):
        if not state.get('user_request'):
            prompt = ChatPromptTemplate.from_messages([{
                'role':'system',
                'content':'''
                You are an expert resume writer and ATS (Applicant Tracking System) specialist.

                Context:
                    {context}

                User Requirement:
                    {requirement}

                Job Description:
                    Instructions:
                    - If its no data is present then leave this field.
                    - If data is provided from user-end then make shure to add all the relevant field details that will make candidate stand-out in croud.
                    {job_description}

                Resume Template Description:
                
                    [Resume Template]
                    ==========================
                    {template}
                    ==========================

                    - Ensure the resume is concise, well-structured, and tailored to the user's requirements.
                    - Highlight achievements and relevant experience.
                    - Use bullet points where appropriate.

                Generate the complete resume that can be converted to pdf and directly be send to recruter.'''}])
           
            input_message_history = False

        if state.get('user_request'):
            prompt = ChatPromptTemplate.from_messages([{'role':'user',
                        'content':'''
                        Analyze user query and make changes to :
                            {user_query}
                            '''},
                            MessagesPlaceholder(variable_name="chat_history")])
            
            input_message_history = True

        # featching relevant doocuments
        retriever = cls.create_vector_db(cls.model, prompt)

        input_data = {
            'requirement' : st.session_state.data_upload['user_requirement'],
            'job_description' : st.session_state.data_upload['job_description'],
            'template' : default(),
            }
        # trim message
        if input_message_history:
            trimmed_history = cls.history_trimmer.invoke(st.session_state.ouput_data['message_data'])
            input_data['chat_history'] = trimmed_history

        # executing
        res = retriever.invoke(input_data)
        st.session_state.ouput_data['message_data'].append(prompt)
        st.session_state.ouput_data['message_data'].append({'role':'assistant', 'content':res.content})

        return {'resume': res.content}
    
    def user_input_interrupt(state: State):
        return State
    
    @classmethod
    def review_agent(cls, state: State):
        prompt = ChatPromptTemplate.from_messages([{'role':'system',
                                                 'content':'You are an hiring expert and have gained exceptional level of experiance in candiate hiring for many companies'}])
        
        model = cls.model.with_structured_output(expert_review_resume)
        res = model.invoke(prompt)
        if res.sentiment == 'Perfect':
            return {'final_resume': res.resume}
            
        elif res.sentiment == 'Improvement Required':
            return {'suggestion': res.suggestion, 'sentiment' : res.sentiment}
            
    def rout_after_reviewagent(state: State):
        if state.get('final_resume'):
            return END
        elif state.get('sentiment') == 'Improvement Required':
            return 'Re-run'
    
    @classmethod
    def sentiment(cls, state: State):
        prompt = ChatPromptTemplate.from_messages([{'role': 'system', 
                                                    'content': f'''
                                                        Analyze the following text and respond if improvement is required or not:
                                                            {state['user_request']}'''}])
        model = cls.model.with_structured_output(response_analysis)
        res = model.invoke(prompt)
        if res.sentiment == 'Perfect':
            return 'Perfect'
        elif res.sentiment == 'Improvement Required':
            return 'Improvement Required'


    @classmethod
    def resume_graph(cls, state:State):
        _graph = (
            StateGraph(state)
            .add_node('Create Resume', cls.create_resume)
            .add_node('User Feedback', cls.user_input_interrupt)
            .add_node('Review Expert', cls.review_agent)

            .add_edge(START, 'Create Resume')
            .add_edge('Create Resume', 'User Feedback')
            .add_edge('User Feedback', cls.sentiment, {'Perfect': 'Review Expert', 'Improvement Required': 'Create Resume'})
            .add_edge('Review Expert', cls.rout_after_reviewagent, {END : END, 'Re-run' : 'Create Resume'})
            .compile(interrupt_before=['User Feedback'], checkpointer = MemorySaver())
        )
        return _graph