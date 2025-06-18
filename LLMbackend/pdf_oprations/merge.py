import streamlit as st
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import io
import base64
from PIL import Image
import fitz  # PyMuPDF for PDF preview
import tempfile
import os

def pdf_to_image(pdf_bytes, page_num=0):
    """Convert PDF page to image for preview"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name
        
        # Open PDF with PyMuPDF
        doc = fitz.open(tmp_file_path)
        page = doc[page_num]
        
        # Render page to image
        mat = fitz.Matrix(1.5, 1.5)  # Scale factor for better quality
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # Clean up
        doc.close()
        os.unlink(tmp_file_path)
        
        return img_data
    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")
        return None

def merge_pdfs(pdf_files_with_positions):
    """Merge PDFs based on their positions"""
    writer = PdfWriter()
    
    # Sort files by position
    sorted_files = sorted(pdf_files_with_positions, key=lambda x: x['position'])
    
    for file_info in sorted_files:
        pdf_bytes = file_info['content']
        reader = PdfReader(io.BytesIO(pdf_bytes))
        
        # Add all pages from this PDF
        for page in reader.pages:
            writer.add_page(page)
    
    # Write to bytes
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    
    return output_buffer.getvalue()

def get_pdf_info(pdf_bytes):
    """Get basic info about PDF"""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return {
            'pages': len(reader.pages),
            'title': reader.metadata.get('/Title', 'Unknown') if reader.metadata else 'Unknown'
        }
    except Exception as e:
        return {'pages': 0, 'title': 'Error reading PDF'}

def main():
    # st.set_page_config(
    #     page_title="PDF Merger Tool",
    #     page_icon="📄",
    #     layout="wide"
    # )
    
    st.header("📄 PDF Merger Tool")
    st.markdown("Upload multiple PDF files, arrange their order, and merge them into a single document.")
    
    # Initialize session state
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'positions' not in st.session_state:
        st.session_state.positions = {}
    
    # File upload section
    st.header("1. Upload PDF Files")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select multiple PDF files to merge"
    )
    
    if uploaded_files:
        # Store uploaded files in session state
        st.session_state.uploaded_files = []
        for file in uploaded_files:
            file_data = {
                'name': file.name,
                'content': file.read(),
                'size': len(file.getvalue())
            }
            st.session_state.uploaded_files.append(file_data)
        
        st.success(f"✅ {len(uploaded_files)} PDF files uploaded successfully!")
        
        # Preview and position section
        if st.session_state.uploaded_files:
            st.header("2. Preview Files & Set Merge Order")
            st.markdown("Preview each PDF and set the position for merging (1 = first, 2 = second, etc.)")
            
            # Create columns for layout
            for i, file_data in enumerate(st.session_state.uploaded_files):
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader(f"📄 {file_data['name']}")
                        
                        # Get PDF info
                        pdf_info = get_pdf_info(file_data['content'])
                        st.write(f"**Pages:** {pdf_info['pages']} | **Size:** {file_data['size']:,} bytes")
                        
                        # Generate preview
                        with st.spinner(f"Generating preview for {file_data['name']}..."):
                            preview_img = pdf_to_image(file_data['content'])
                            
                        if preview_img:
                            st.image(preview_img, caption=f"Preview of {file_data['name']} (Page 1)", width=400)
                        else:
                            st.warning("⚠️ Could not generate preview for this file")
                    
                    with col2:
                        st.markdown("### Position Settings")
                        
                        # Position input
                        default_pos = st.session_state.positions.get(file_data['name'], i + 1)
                        position = st.number_input(
                            f"Position for {file_data['name'][:20]}...",
                            min_value=1,
                            max_value=len(st.session_state.uploaded_files),
                            value=default_pos,
                            key=f"pos_{i}",
                            help="Set the order for merging (1 = first)"
                        )
                        
                        st.session_state.positions[file_data['name']] = position
                        
                        # Show current position
                        st.info(f"📍 Position: {position}")
                
                st.divider()
            
            # Merge section
            st.header("3. Merge PDFs")
            
            # Show merge order
            files_with_positions = []
            for file_data in st.session_state.uploaded_files:
                position = st.session_state.positions.get(file_data['name'], 1)
                files_with_positions.append({
                    'name': file_data['name'],
                    'content': file_data['content'],
                    'position': position
                })
            
            # Sort and display merge order
            sorted_files = sorted(files_with_positions, key=lambda x: x['position'])
            
            st.subheader("📋 Merge Order:")
            for i, file_info in enumerate(sorted_files, 1):
                st.write(f"{i}. **{file_info['name']}** (Position: {file_info['position']})")
            
            # Check for duplicate positions
            positions = [f['position'] for f in files_with_positions]
            if len(positions) != len(set(positions)):
                st.warning("⚠️ Warning: Some files have the same position. They will be merged in upload order for duplicate positions.")
            
            # Merge button
            if st.button("🔄 Merge PDFs", type="primary", use_container_width=True):
                try:
                    with st.spinner("Merging PDFs..."):
                        merged_pdf = merge_pdfs(files_with_positions)
                    
                    st.success("✅ PDFs merged successfully!")
                    
                    # Download section
                    st.header("4. Download Merged PDF")
                    
                    # Generate filename
                    merged_filename = f"merged_pdf_{len(st.session_state.uploaded_files)}_files.pdf"
                    
                    # Create download button
                    st.download_button(
                        label="📥 Download Merged PDF",
                        data=merged_pdf,
                        file_name=merged_filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # Show merged PDF info
                    merged_info = get_pdf_info(merged_pdf)
                    st.info(f"📊 Merged PDF: {merged_info['pages']} total pages, {len(merged_pdf):,} bytes")
                    
                except Exception as e:
                    st.error(f"❌ Error merging PDFs: {str(e)}")
    
    else:
        st.info("👆 Please upload PDF files to get started")
    
    # Instructions
    with st.sidebar:
        st.header("📖 Instructions")
        st.markdown("""
        ### How to use:
        
        1. **Upload Files**: Click "Browse files" and select multiple PDF files
        
        2. **Preview & Order**: 
           - View preview of each PDF
           - Set position numbers (1, 2, 3, etc.)
           - Lower numbers appear first in merged PDF
        
        3. **Merge**: Click "Merge PDFs" to combine files
        
        4. **Download**: Save the merged PDF to your device
        
        ### Tips:
        - You can upload up to multiple PDFs at once
        - Position numbers determine merge order
        - Preview shows the first page of each PDF
        - File size and page count are displayed
        """)
        
        # st.header("🔧 Requirements")
        # st.code("""
        # pip install streamlit
        # pip install PyPDF2
        # pip install PyMuPDF
        # pip install Pillow
        # """)

