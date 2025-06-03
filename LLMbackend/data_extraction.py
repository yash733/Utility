from PyPDF2 import PdfReader
import docx
import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from langchain.text_splitter import RecursiveCharacterTextSplitter

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
        data_track.info(f'pdf data {text} ')
        return text
    
    def data_txt(file):
        text = file.read().decode("utf-8")
        data_track.info(f'txt data {text}')
        return text

    def data_docx(file):
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraph])
        data_track.info(f'docx data {text}')
        return text

    @staticmethod
    def resume_data_extraction():
        data_to_update = {}
        pdf_data, txt_data, docx_data = {}, {}, {}

        # Input Method
        option = st.radio(label='Select Input format', options = ['Upload Existing Resume or Content', 'Add data in text box'])
        if option == 'Upload Existing Resume or Content':
            # log
            data_track.info('Upload Existing Resume or Content')

            files = st.file_uploader(label='Enter your Resumme to Impprove or To create one add file with content', 
                                     type=['pdf','txt','docx'], accept_multiple_files = True)
            
            # Loading Data
            # Also can handle multiple docs @Future Enabled
            if files:
                # log
                data_track.info('file uploaded')

                for file in files:
                    with st.expander(label=f'What does {file.name} represents ?' ,expanded=True):
                        data_representation = st.radio(label= 'Select what this document represents',
                                                       options=['Resume', 'CV', 'Profile Detail', 'Acchievement/Accomplishment', 'Meta Data'],
                                                       index=None,
                                                       key=f"label_{file.name}")
                        if not data_representation:
                            st.stop()

                    if file.name.lower().endswith('.pdf'):
                        # pdf
                        pdf_data.update({file.name : {'content' : data_extraction.data_pdf(file), 
                                                      'data_representation':data_representation}})
                        
                    elif file.name.lower().endswith('.txt'):
                        # txt
                        txt_data.update({file.name : {'content' : data_extraction.data_txt(file), 
                                                      'data_representation':data_representation}})
                        
                    elif file.name.lower().endswith('.docx'):   
                        # docx
                        docx_data.update({file.name : {'content' : data_extraction.data_docx(file), 
                                                       'data_representation':data_representation}})
                
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
                        
            else:
                st.warning("Kindly upload an existing Resume or Context to create/improve Resume !")
                st.stop()
        
        elif option == 'Add data in text box':
            text_data = st.text_area(label='Enter Content for creating/improving Resume')
            data_track.info('Add data in text box')

            if text_data:
                # log
                data_track.info('text recieved')
                
                with st.expander('Loaded Data', expanded = True):
                    # log
                    data_track.info(f'data loaded in session_state')
                    st.session_state.data_uploaded.update({'data':{'text_data':text_data}})
                    text = st.session_state.data_uploaded['data'].get('text_data')
                    st.write(text[:500])

        else:
            st.warning('Kindly select an Option')
            st.stop()

        with st.expander('Load Meta Data', expanded=True):
            #log 
            data_track.info('Meta Data')

            jd_data = st.text_area('Job Discription')
            if jd_data and st.button('Save', key = 'Jd_data'):
                st.session_state.data_uploaded.update({'job_description':jd_data})
                data_track.info('JD added')

            template_data = st.text_area('Template description')
            if template_data and st.button('Save', key= 'temp_data'):
                data_track.info('Template added')
                st.session_state.data_upload.update({'template_data':template_data})
    
    @staticmethod
    def data_flatning():
        documents = list()
        for key, value in st.session_state.data_uploaded['data'].items():
            for file_key, file_value in value.items():
                content = file_value.get('content')
                data_represts = file_value.get('data_representation')
                file_name = file_key

            text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
            
            # ----- Creating Object based Document ----- #
            chunks = text_splitter.create_documents([content])

            for chunk in chunks:
                # ----- Adding Metatadata into Object based Document ----- #
                chunk.metadata = {'file_name':file_name, 'data_representation':data_represts}
                documents.append(chunk)
        
        return documents