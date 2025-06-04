import streamlit as st
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import creacreate_retrieval_chain
from langchain_core.messages.utils import trim_messages

from data_extraction import data_extraction
from config.resume_template import default

class agents:
    model = st.session_state.user_selection['llm_model']
    
    def create_vector_db(model, prompt):
        embedding = OllamaEmbeddings(model="nomic-embed-text:v1.5")
        
        reduced_document = data_extraction.data_flatning()
        # vectorstore will hold important data @files
        vectore_store = FAISS.from_documents(documents=reduced_document, embedding=embedding)
        retriever = vectore_store.as_retriever()

        doc_chain = create_stuff_documents_chain(model, prompt)
        relevant_info = creacreate_retrieval_chain(doc_chain, retriever)
        return relevant_info

    @classmethod
    def create_resume(cls):
        system_message = {
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

                Generate the complete resume that can be converted to pdf and directly be send to recruter.'''}
        
        if not st.session_state.output_data['improvement_request']:
            prompt = ChatPromptTemplate.from_messages([system_message, MessagesPlaceholder(variable_name="chat_history")])
        
        # chat history
        st.session_state.ouput_data['message_data'].append(system_message)

        # featching relevant doocuments
        retriever = cls.create_vector_db(cls.model, prompt)
        
        # trim message
        trimmer = trim_messages(
            max_tokens = 500,
            strategy = 'last',
            token_counter = cls.model,
            start_on = 'system',
            inclue_system = True,
            allow_partial = False
        )

        trimmed_history = trimmer.invoke(st.session_state.ouput_data['message_data'])

        # executing
        res = retriever.invoke({
            'requirement' : st.session_state.data_upload['user_requirement'],
            'job_description' : st.session_state.data_upload['job_description'],
            'template' : default(),
            'chat_history' : trimmed_history
        })
        


            
