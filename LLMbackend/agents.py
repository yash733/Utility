import streamlit as st
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.messages.utils import trim_messages
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from data_extraction import data_extraction
from config.resume_template import default
from config.variable_validation import State, response_analysis, expert_review_resume

class vector_db:
    _vector_db = None

    @classmethod
    def create_vector_db(cls):
        if cls._vector_db == None:
            embedding = OllamaEmbeddings(model="nomic-embed-text:v1.5")
            
            reduced_document = data_extraction.data_flatning()
            # vectorstore will hold important data @files
            cls._vectore_db = FAISS.from_documents(documents=reduced_document, embedding=embedding)
    
    @classmethod
    def get_retrieval_chain(cls, model, prompt):
        retriever = cls._vectore_db.as_retriever()
        doc_chain = create_stuff_documents_chain(model, prompt)
        return create_retrieval_chain(doc_chain, retriever)
    

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
    
    # ========================================= #

    @classmethod
    def create_resume(cls, state: State):
        # === First RUN === #
        if st.session_state.state == 'START': # State tracking
            system = {'role':'system',
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

                Generate the complete resume that can be converted to pdf and directly be send to recruter.'''}
            
            prompt = ChatPromptTemplate.from_messages([system])
           
            input_data = {'requirement' : State.get('user_request'),
                          'job_description' : st.session_state.data_upload['job_description'],
                          'template' : default()}

        # === Loop RUN === #
        if st.session_state.state == 'Interrupt':
            system = {'role':'system',
                        'content':'''
                        Changes requested by User:
                            {user_suggestion}

                        Current Resume:
                            {resume}

                        Job Description:
                            {jobdesc}

                        Analyze user query carefully and make the requested changes to the resume, while being relevent to Job Description,
                        also remember to make it ready to use, by conveing the data directly to pdf format.
                        '''}
            
            prompt = ChatPromptTemplate.from_messages([system, MessagesPlaceholder(variable_name="chat_history")])
            
            # Trim Message
            trimmed_history = cls.history_trimmer.invoke(st.session_state.ouput_data['message_data'])
            input_data = {'user_suggestion' : State.get('user_suggestion'),
                          'resume' : State.get('resume'),
                          'jobdesc' : st.session_state.data_upload['job_description'],
                          'chat_history' : trimmed_history}
            
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
            trimmed_history = cls.history_trimmer.invoke(st.session_state.ouput_data['message_data'])
            input_data = {'expert' : expert_review_resume.get('suggestion'),
                          'resume' : State.get('resume'),
                          'chat_history' : trimmed_history}
            
        # featching relevant doocuments
        retrieval_chain = vector_db.get_retrieval_chain(cls.model, prompt)            

        # executing
        result = retrieval_chain.invoke(input_data)
        st.session_state.ouput_data['message_data'].append(system)
        st.session_state.ouput_data['message_data'].append({'role':'assistant', 'content':result.content})

        return {'resume': result.content}
    
    # -----------------------------------------------
    def user_input_interrupt(state: State):
        st.session_state.state = 'Interrupt' # State tracking
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
                    {jobdesc}

                You are an hiring expert and have gained exceptional level of experiance in hiring most suitable candidates.
                Analyze the resume and provide your take allowing the resume more job description centric.'''}
        
        prompt = ChatPromptTemplate.from_messages([system, MessagesPlaceholder(variable_name='chat_history')])

        model = cls.model.with_structured_output(expert_review_resume)
        retrieval_chain = vector_db.get_retrieval_chain(model, prompt)

        # trimme message history
        trimmed_history = cls.history_trimmer.invoke(st.session_state.ouput_data['message_data'])
        
        input_data = {'resume' : State.get('resume'),
                      'jobdesc' : st.session_state.data_upload['job_description'],
                      'chat_history' : trimmed_history
                      }
                
        res = retrieval_chain.invoke(input_data)

        if res.sentiment == 'Perfect':
            return {'final_resume': res.resume}
            
        elif res.sentiment == 'Improvement Required':
            return {'suggestion': res.suggestion, 
                    'sentiment' : res.sentiment, 
                    'resume' : res.resume}
        
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

    @classmethod
    def resume_graph(cls, state):
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