from PyPDF2 import PdfReader
import docx
import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.resume_template import default
from logger.logg_rep import logging

data_track = logging.getLogger('Data-Flow')
data_track.setLevel(logging.DEBUG)

class data_extraction:
    '''
    File Extension	MIME Type (file.type)
    .pdf          	application/pdf
    .txt	        text/plain
    .docx	        application/vnd.openxmlformats-officedocument.wordprocessingml.document
    '''
    
    def data_pdf(file):
        raw_data = PdfReader(file)
        text = ''
        for page in raw_data.pages:
            text += page.extract_text()
        data_track.info(f'pdf data {text} ') # log
        return text
    
    def data_txt(file):
        text = file.read().decode("utf-8")
        data_track.info(f'txt data {text}') # log
        return text

    def data_docx(file):
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraph])
        data_track.info(f'docx data {text}') # log
        return text

    @staticmethod
    def resume_data_extraction():
        if st.session_state.get('data_loaded'):
            return
        
        data_to_update = {}
        pdf_data, txt_data, docx_data = {}, {}, {}

        # Input Method
        option = st.radio(label='Select Input format', options = ['Upload Existing Resume or Content', 'Add data in text box'])
        if option == 'Upload Existing Resume or Content':
            # log
            data_track.info('Upload Existing Resume or Content') # log

            files = st.file_uploader(label='Enter your Resumme to Impprove or To create one add file with content', 
                                     type=['pdf','txt','docx'], accept_multiple_files = True)
            
            # Loading Data
            # Also can handle multiple docs @Future Enabled
            if files:
                # log
                data_track.info('file uploaded')

                for file in files:
                    with st.expander(label=f'What does {file.name} represents ?' ,expanded=True):
                        data_representation = st.radio(label= "d", label_visibility = 'collapsed',
                                                       options=['Resume', 'CV', 'Profile Detail', 'Acchievement/Accomplishment', 'Meta Data'],
                                                       index=None,
                                                       key=f"label_{file.name}")
                        if not data_representation:
                            st.stop()
                    
                    if file.name.lower().endswith('.pdf'):
                        # pdf
                        pdf_data.update({file.name : {'content' : data_extraction.data_pdf(file), 
                                                    'data_representation':data_representation}})
                        # log
                        data_track.info('Updated pdf_data')

                    elif file.name.lower().endswith('.txt'):
                        # txt
                        txt_data.update({file.name : {'content' : data_extraction.data_txt(file), 
                                                    'data_representation':data_representation}})
                        # log
                        data_track.info('Updated txt_data')

                    elif file.name.lower().endswith('.docx'):   
                        # docx
                        docx_data.update({file.name : {'content' : data_extraction.data_docx(file), 
                                                    'data_representation':data_representation}})
                        # log
                        data_track.info('Updated docx_data')
                    
                    # else: Not needed as no other file format can be uploaded

                data_to_update = {}
                # Saving Loaded Data
                if pdf_data:
                    data_to_update['pdf_data'] = pdf_data
                if txt_data:
                    data_to_update['txt_data'] = txt_data
                if docx_data:
                    data_to_update['docx_data'] = docx_data
                
                with st.expander('Loaded Data', expanded = False):
                    #log
                    data_track.info(f'data loaded in session_state')

                    # ----- Update Session_State with extracted data ----- #
                    st.session_state.data_uploaded.update({'data':data_to_update})
                    st.write(st.session_state.data_uploaded['data'])
                st.session_state['data_loaded'] = True
                        
            else:
                data_track.error('No file uploaded')
                st.warning("Kindly upload an existing Resume or Context to create/improve Resume !")
                st.stop()
        
        elif option == 'Add data in text box':
            text_data = st.text_area(label='Enter Content for creating Resume')
            data_track.info('Add data in text box')

            if text_data:
                # log
                data_track.info('text recieved')
                
                with st.expander('Loaded Data', expanded = True):
                    # log
                    data_track.info(f'data loaded in session_state')
                    st.session_state.data_uploaded.update({'data':{
                                                                'text_input':{
                                                                    'text':{
                                                                        'content':text_data}}}})
                    
                    text = st.session_state.data_uploaded['data'].get('text_data')
                    st.write(text)

                with st.expander(label='What does input text represents ?' ,expanded=True):
                    data_representation = st.radio(label= 'Select what this data represents',
                                                    options=['Resume', 'CV', 'Profile Detail', 'Acchievement/Accomplishment', 'Meta Data'],
                                                    index=None,
                                                    key=f"label_txt_input")

        else:
            st.warning('Kindly select an Option')
            st.stop()

        with st.expander('Load Meta Data', expanded=True):
            # log 
            data_track.info('Meta Data')

            jd_data = st.text_input('Job Discription')
            template_data = st.text_area('Resume Template', value = default())
            st.stop()
            if st.button('Save', key = 'Meta Data'):
                if jd_data:
                    st.session_state.data_uploaded.update({'job_description':jd_data})
                    # log
                    data_track.info('JD added')
                if template_data:
                    # log
                    data_track.info('Template added')
                    st.session_state.data_uploaded.update({'template_data':template_data})
    
    @staticmethod
    def data_flatning():
        documents = list()
        for key, value in st.session_state.data_uploaded['data'].items():
            for file_key, file_value in value.items():
                content = file_value.get('content')
                data_represts = file_value.get('data_representation')
                file_name = file_key

            text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
            # log
            data_track.info('Data divided into chunks')

            # ----- Creating Object based Document ----- #
            chunks = text_splitter.create_documents([content])
            # log
            data_track.info('converted uploaded data into object type')

            for chunk in chunks:
                # ----- Adding Metatadata into Object based Document ----- #
                chunk.metadata = {'file_name':file_name, 'data_representation':data_represts}
                documents.append(chunk)
            # log 
            data_track.info('Attached Meta data to each chunk of data')
        
        return documents