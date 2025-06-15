import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

import streamlit as st
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.messages.utils import trim_messages
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from LLMbackend.data_extraction import data_extraction
from config.resume_template import default
from config.variable_validation import State, response_analysis, expert_review_resume
from logger.logg_rep import logging

# ===============================
log = logging.getLogger('Graph')
log.setLevel(logging.DEBUG)
# ===============================

class vector_db:
    _vector_db = None

    @classmethod
    def create_vector_db(cls):
        if cls._vector_db == None:
            embedding = OllamaEmbeddings(model="nomic-embed-text:v1.5")
            reduced_document = data_extraction.data_flatning()
            # vectorstore will hold important data @files
            cls._vectore_db = FAISS.from_documents(documents=reduced_document, embedding=embedding)
            log.info('Vector_DB created') # log

    @classmethod
    def get_retrieval_chain(cls, model, prompt):
        if model == None:
            raise ValueError("Model cannot be None")
        
        vector_db.create_vector_db()
        log.info('Featching Relevant information from vectordb') # log
        retriever = cls._vectore_db.as_retriever(search_kwargs={'k': 15})
        doc_chain = create_stuff_documents_chain(llm = model,
                                                 prompt = prompt, 
                                                 document_variable_name = "context")
        return create_retrieval_chain(combine_docs_chain = doc_chain, 
                                      retriever = retriever)
    
class agents:
    model = None
  
    @classmethod
    def initialize_model(cls):
        if cls.model is None:
            try:
                cls.model = st.session_state.user_selection.get('llm_model')
                if cls.model is None:
                    raise ValueError("No model found in session state")
                    
                # Test connection
                res = cls.model.invoke('testing connection')
                log.info(f'Model test response: {res}')
                return cls.model
            
            except Exception as e:
                log.error(f'Model initialization failed: {e}')
                st.error('Failed to initialize LLM model')
                return None

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
        log.info('History trimmed') # log
        return trimmer
    
    # ========================================= #

    @classmethod
    def resume_maker(cls, state: State):
        # Initialize model first
        if cls.model is None:
            cls.initialize_model()
            if cls.model is None:
                raise ValueError("Failed to initialize model")
        
        if not st.session_state.output_data.get('message_data'):
            st.session_state.output_data['message_data'] = []

        # === First RUN === #
        if st.session_state.state == 'START': # State tracking
            st.session_state.state = 'Create_Resume'
            system = {'role':'system',
                'content':'''
                You are an expert resume writer and ATS (Applicant Tracking System) specialist.

                Context:
                    {context}

                User Requirement:
                    {input}

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

                    - Ensure the resume is concise, well-structured, and tailored to the user's inputs.
                    - Highlight achievements and relevant experience.
                    - Use bullet points where appropriate.

                Generate the complete resume that can be converted to pdf and directly be send to recruter.'''}
            
            prompt = ChatPromptTemplate.from_messages([system])
           
            input_data = {'input' : state.get('user_requirement'),
                          'job_description' : st.session_state.data_uploaded.get('job_description'),
                          'template' : st.session_state.template_data}
            log.info('Prompt 1') # log

        # === Loop RUN === #
        if st.session_state.state == 'Interrupt':
            system = {'role':'system',
                        'content':'''
                        Changes requested by User:
                            {input}

                        Current Resume:
                            {resume}

                        Job Description:
                            {job_description}

                        Analyze user query carefully and make the requested changes to the resume, while being relevent to Job Description,
                        also remember to make it ready to use, by conveing the data directly to pdf format.
                        '''}
            
            prompt = ChatPromptTemplate.from_messages([system, MessagesPlaceholder(variable_name="chat_history")])
            
            # Trim Message
            trimmed_history = cls.history_trimmer.invoke(st.session_state.output_data['message_data'])
            input_data = {'input' : state.get('user_suggestion'),
                          'resume' : state.get('resume'),
                          'job_description' : st.session_state.data_uploaded.get('job_description'),
                          'chat_history' : trimmed_history}
            log.info('Prompt 2 Interrupt') # log

        # === Loop RUN === #
        if st.session_state.state == 'Agent':
            system = {'role':'system',
                    'content': '''
                    Context:
                        {context}

                    Changes suggested by Hiring Expert:
                        {expert}
                        
                    Current Resume:
                        {resume}
                    
                    Make necesary changes to reume, following the suggestion/instruction provided by Hiring Expert, you can access relevant information from context.
                    '''}
            
            prompt = ChatPromptTemplate.from_messages([system, MessagesPlaceholder(variable_name="chat_history")])
            # Trim Message
            trimmed_history = cls.history_trimmer.invoke(st.session_state.output_data['message_data'])
            input_data = {'expert' : expert_review_resume.get('suggestion'),
                          'resume' : State.get('resume'),
                          'chat_history' : trimmed_history}
            log.info('Prompt 3 Agent') # log

        # featching relevant doocuments
        retrieval_chain = vector_db.get_retrieval_chain(cls.model, prompt)            

        # executing
        result = retrieval_chain.invoke(input_data)
        st.session_state.output_data['message_data'].append(system)
        st.session_state.output_data['message_data'].append({'role':'assistant', 'content':result.content})

        return {'resume': result.content}
    
    # -----------------------------------------------
    def user_input_interrupt(state: State):
        st.session_state.state = 'Interrupt' # State tracking
        log.info('User Interrupt') # log
        return State
    
    # -----------------------------------------------
    @classmethod
    def review_agent(cls, state: State):
        st.session_state.state = 'Agent' # State tracking

        system = {'role':'system',
                'content':'''
                More Information:
                    {context}

                Resume:
                    {resume}

                Job Description:
                    {job_description if job_description else 'No job description is provied by user end'}

                You are an hiring expert and have gained exceptional level of experiance in hiring most suitable candidates.
                Analyze the resume and provide your take allowing the resume more job description centric.'''}
        
        prompt = ChatPromptTemplate.from_messages([system, MessagesPlaceholder(variable_name='chat_history')])

        model = cls.model.with_structured_output(expert_review_resume)
        retrieval_chain = vector_db.get_retrieval_chain(model, prompt)

        # trimme message history
        trimmed_history = cls.history_trimmer.invoke(st.session_state.output_data['message_data'])

        input_data = {'resume' : state.get('resume'),
                      'job_description' : st.session_state.data_uploaded.get('job_description'),
                      'chat_history' : trimmed_history
                      }
                
        result = retrieval_chain.invoke(input_data)

        st.session_state.output_data['message_data'].append(system)
        st.session_state.output_data['message_data'].append({'role':'assistant', 'content':result.content})

        if result.sentiment == 'Perfect':
            log.info('Review Agent - Final Resume') # log
            return {'final_resume': result.resume}
            
        elif result.sentiment == 'Improvement Required':
            log.info('Review Agent - Improvent is required') # log
            return {'suggestion': result.suggestion, 
                    'sentiment' : result.sentiment, 
                    'resume' : result.resume}
        
    # -----------------------------------------------            
    def rout_after_reviewagent(state: State):
        if state.get('final_resume'):
            return END
        elif state.get('sentiment') == 'Improvement Required':
            return 'Re-run'
    
    # -----------------------------------------------
    @classmethod
    def sentiment(cls, state: State):
        prompt = ChatPromptTemplate.from_messages([{'role': 'system', 
                                                    'content': f'''
                                                        Analyze the following text and respond if improvement is required or not:
                                                            {state['user_suggestion']}'''}])
        model = cls.model.with_structured_output(response_analysis)
        res = model.invoke(prompt)
        if res.sentiment == 'Perfect':
            return 'Perfect'
        elif res.sentiment == 'Improvement Required':
            return 'Improvement Required'


    # *********************************************** #
    '''
    +--------+
    | Start  |
    +--------+
        |
        v
    +-------------+
    | 1st Draft   |
    +-------------+
          |
          v
    +-------------+
    |   Review    |
    +-------------+
        |       |
        |       v
        |     +--------+
        |     | Poor   |
        |     +--------+
        |         |
        |         v
        |     +-------------+
        |     | 1st Draft   |
        |     +-------------+
        v
    +------------------+
    | Expert Review    |
    +------------------+
        |         |
        |         v
        |     +--------+
        |     | Poor   |         Note: As LLMs are not that reliable 
        |     +--------+     *"Not Taking and keeping human in the loop"*
        |         |
        |         v
        |     +-------------+
        |     | 1st Draft   |
        |     +-------------+
        v
    +--------+
    |  End   |
    +--------+
    '''
    @classmethod
    def resume_graph(cls, state):
        _graph = (
            StateGraph(state)
            .add_node('Resume Maker', cls.resume_maker)
            .add_node('User Feedback', cls.user_input_interrupt)
            .add_node('Review Expert', cls.review_agent)

            .add_edge(START, 'Resume Maker')
            .add_edge('Resume Maker', 'User Feedback')
            .add_conditional_edges('User Feedback', cls.sentiment, {'Perfect': 'Review Expert', 'Improvement Required': 'Resume Maker'})
            .add_conditional_edges('Review Expert', cls.rout_after_reviewagent, {END : END, 'Re-run' : 'Resume Maker'})
            .compile(interrupt_before=['User Feedback'], checkpointer = MemorySaver())
        )
        return _graph