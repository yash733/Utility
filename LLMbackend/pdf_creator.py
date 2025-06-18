from fpdf import FPDF
import textwrap
import os
from datetime import datetime
from logger.logg_rep import logging

log = logging.getLogger('PDF-Utils')

def save_resume_as_pdf(resume_content: str, output_dir: str = "generated_resumes") -> str:
    """
    Save resume content as PDF file with proper formatting
    
    Args:
        resume_content: Resume text content
        output_dir: Directory to save PDF files
    
    Returns:
        str: Path to saved PDF file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Set font for headers
        pdf.set_font("Arial", "B", 16)
        
        # Calculate margins and usable width
        margin = 15
        page_width = pdf.w - 2 * margin
        
        # Process content
        sections = resume_content.split('\n\n')
        for section in sections:
            if section.strip():
                # Check if section is a header
                if any(keyword in section.lower() for keyword in 
                    ['summary', 'experience', 'education', 'skills', 'projects']):
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, section.strip(), ln=True)
                    pdf.set_font("Arial", "", 12)
                else:
                    # Wrap text to fit page width
                    wrapped_text = textwrap.fill(section.strip(), width=75)
                    for line in wrapped_text.split('\n'):
                        pdf.multi_cell(0, 10, line)
                pdf.ln(5)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Save PDF
        pdf.output(filepath)
        log.info(f"Resume saved as PDF: {filepath}")
        return filepath
        
    except Exception as e:
        log.error(f"Error saving PDF: {str(e)}")
        raise