import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

import streamlit as st
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.messages import trim_messages
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from LLMbackend.data_extraction import data_extraction
from config.variable_validation import State, response_analysis, expert_review_resume, output_fmt
from logger.logg_rep import logging
from config.prompts import interrupt_, review_agent_to_create_resume, start_create_resume, review_agent

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
        retriever = cls._vectore_db.as_retriever(search_kwargs={'k': 10}, 
                                                 similarity_score_threshold = 0.3)
        doc_chain = create_stuff_documents_chain(llm = model,
                                                 prompt = prompt, 
                                                 document_variable_name = "context")
        return create_retrieval_chain(combine_docs_chain = doc_chain, 
                                      retriever = retriever)

def result_Message_history(result):
    answer = result.get("answer")
    if hasattr(answer, "resume"):
        content = answer.resume
        if answer.meta_data:
            content += f"\n\n---\n**Meta:** {answer.meta_data}"
    else:
        content = answer
    return content

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
    def history_trimmer(cls, messages, token_size = 400):
        trimme_message = trim_messages( 
            messages,
            max_tokens = token_size,
            strategy = 'last',
            token_counter = cls.model,
            start_on = 'system',
            allow_partial = False
            )
        log.info('History trimmed') # log
        return trimme_message 
    
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
            
            system = start_create_resume.prompt()
            prompt = ChatPromptTemplate.from_messages([system])
            log.info('Prompt 1') # log

            input_data = {'input' : state.get('user_requirement'),
                          'job_description' : st.session_state.data_uploaded.get('job_description'),
                          'template' : st.session_state.data_uploaded.get('template_data')}
            
        # === Loop RUN === #
        elif st.session_state.state == 'Interrupt':
            system = interrupt_.prompt()
            
            prompt = ChatPromptTemplate.from_messages([system, MessagesPlaceholder(variable_name="chat_history")])
            log.info('Prompt 2 Interrupt') # log
            log.debug(f'resume - {state.get("resume")}')

            # Trim Message
            trimmed_history = cls.history_trimmer(st.session_state.output_data['message_data'])
            input_data = {'input' : state.get('user_suggestion'),
                          'resume' : state.get('resume'),
                          'job_description' : st.session_state.data_uploaded.get('job_description'),
                          'chat_history' : trimmed_history}

        # === Loop RUN === #
        elif st.session_state.state == 'Agent':
            system = review_agent_to_create_resume.prompt()
            
            prompt = ChatPromptTemplate.from_messages([system, MessagesPlaceholder(variable_name="chat_history")])
            log.info('Prompt 3 Agent') # log

            # Trim Message
            trimmed_history = cls.history_trimmer(st.session_state.output_data['message_data'])
            input_data = {'input' : state.get('suggestion'),
                          'resume' : state.get('resume'),
                          'chat_history' : trimmed_history}
        
        # structured output Resume + Meta Data
        model = cls.model.with_structured_output(output_fmt)
        # featching relevant doocuments
        retrieval_chain = vector_db.get_retrieval_chain(model, prompt)            

        # executing
        result = retrieval_chain.invoke(input_data)
        log.info(f'result , {result}') # log
        log.debug(f'Output 1 - {result.get("answer").resume}') # log

        # Message History
        content = result_Message_history(result)
        st.session_state.output_data['message_data'].append(system)
        st.session_state.output_data['message_data'].append({'role': 'assistant', 'content': content})
        
        log.info(f'State {st.session_state.state}') # log
        
        st.session_state.state = 'Create_Resume'
        return {'resume': result.get("answer").resume}
    
    # -----------------------------------------------
    def user_input_interrupt(state: State):
        st.session_state.state = 'Interrupt' # State tracking
        log.info('User Interrupt') # log
        return state
    
    # -----------------------------------------------
    @classmethod
    def review_agent(cls, state: State):
        st.session_state.state = 'Agent' # State tracking

        system = review_agent.prompt()

        prompt = ChatPromptTemplate.from_messages([system, MessagesPlaceholder(variable_name='chat_history')])

        model = cls.model.with_structured_output(expert_review_resume)
        retrieval_chain = vector_db.get_retrieval_chain(model, prompt)

        # trimme message history
        trimmed_history = cls.history_trimmer(st.session_state.output_data['message_data'])
        job_desc = st.session_state.data_uploaded.get('job_description', "No Job description provided")

        input_data = {'input' : state.get('resume'),
                      'job_description' : job_desc,
                      'chat_history' : trimmed_history
                      }
                
        result = retrieval_chain.invoke(input_data)
        log.debug(f'Review Agent - {result}') # log

        # ---- Message History ---- 
        content = result_Message_history(result)
        st.session_state.output_data['message_data'].append(system)
        st.session_state.output_data['message_data'].append({'role': 'assistant', 'content': content})
        
        output = result.get('answer')
        if output.sentiment == 'Perfect':
            log.info('Review Agent - Final Resume') # log
            return {'final_resume': result.get('resume')}
            
        elif output.sentiment == 'Improvement Required':
            log.info('Review Agent - Improvent is required') # log
            return {'suggestion': result.get('suggestion'), 
                    'sentiment' : result.get('sentiment'), 
                    'resume' : result.get('resume')}
        
    # -----------------------------------------------            
    def rout_after_reviewagent(state: State):
        log.debug('re-rout after_reviewagent') # log
        if state.get('final_resume'):
            return END
        elif state.get('sentiment') == 'Improvement Required':
            return 'Re-run'
    
    # -----------------------------------------------
    @classmethod
    def sentiment(cls, state: State):
        log.debug('Sentiment-After-Interrupt') # log
        prompt = ChatPromptTemplate.from_messages([{'role': 'system', 
                'content': """
                Analyze the user's feedback about a resume and classify their sentiment.
            
            User Feedback: {suggestion}
            
            CLASSIFICATION LOGIC:
            
            Return 'Perfect' if the user:
            ✓ Shows satisfaction: "good", "great", "perfect", "excellent", "nice", "looks good"
            ✓ Wants to proceed: "ok", "okay", "fine", "proceed", "next", "continue", "done", "move on"
            ✓ Gives approval: "yes", "correct", "right", "approve", "accept"
            ✓ Uses brief positive terms without requesting changes
            
            Return 'Improvement Required' if the user:
            ✗ Requests changes: "change", "modify", "alter", "fix", "update", "adjust"
            ✗ Wants improvements: "improve", "better", "enhance", "add", "remove", "include"
            ✗ Shows dissatisfaction: "not good", "bad", "needs work", "lacking"
            ✗ Asks specific questions about modifications
            ✗ Provides detailed feedback suggesting alterations
            
            EXAMPLES:
            "" → Perfect
            "ok" → Perfect
            "looks good" → Perfect  
            "proceed" → Perfect
            "can you add more skills?" → Improvement Required
            "change the format" → Improvement Required
            "it needs work" → Improvement Required
            
            Respond with ONLY: 'Perfect' or 'Improvement Required'
                """}])
        
        log.debug(f'Graph User suggestion - {state["user_suggestion"]}') # log
        
        chain = prompt | cls.model.with_structured_output(response_analysis)
        response = chain.invoke({
            'suggestion' : state['user_suggestion']})

        log.debug(f'Sentiment analysis result: {response.sentiment}')
                #  f'(confidence: {response.confidence:.2f}) - {response.reasoning}') #log
        
        if response.sentiment == 'Perfect':
            return 'Perfect'
        elif response.sentiment == 'Improvement Required':
            return 'Improvement Required'

    # ---------------------------------------------
    @classmethod
    def pdf_convert(cls, state = State):
        log.info("Final PDF Conversion") # log
        output_dir = os.join(os.path.dirname(__file__),'..') # Parent folder
        os.makedirs(output_dir, exist_ok = True)


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