# 🧰 Personal Utility Tools

A multi-utility Streamlit application for resume creation, improvement, PDF merging, and more—powered by LLMs (Groq, Ollama) and advanced data extraction.

## 📫 **Causion**
    - The output quality Heavily Depends on the LLM you use.
    - Deepseak model is highly inconsistent NOT RECOMMENDED
---

## Features

### **Create Resume:**  
[X_Post_Showcasing_Working](https://x.com/i/status/1938668567987397080)<br>
[Youtube_](https://www.youtube.com/watch?v=J79F2RcbWZg)<br>

- **Expert Feedback Integration:**  
  Incorporate hiring manager feedback and optimize for ATS (Applicant Tracking Systems).

- **Job Description Tailoring:**  
  Emphasize relevant skills and experience based on job descriptions.

- **Markdown to PDF:**  
  Convert markdown resumes to PDF with proper formatting.

- **Flexible Input:**  
  Upload resumes as PDF, DOCX, TXT, or enter text directly.

- **Session State Management:**  
  All user data and workflow progress are managed in session state for a seamless experience.

![pg1](https://github.com/user-attachments/assets/b33a95b0-5b8b-49fa-9285-a48b4f062788)
![pg2](https://github.com/user-attachments/assets/b0ecad74-dd69-4b63-b709-36351985a60f)
![pg3](https://github.com/user-attachments/assets/0d2abb0f-2bae-49e3-b6a4-cb92f4007f80)
![pg4](https://github.com/user-attachments/assets/4719ce43-767b-440e-a1ef-9dcd454598d4)
![flow_chart](https://github.com/user-attachments/assets/17e043f9-c933-4c50-a623-9f9704b87c13)

---
### **PDF Merge:**  
  Merge multiple PDF files, preview, and download the result.  
![pg1](https://github.com/user-attachments/assets/8dc7656f-dfac-4369-b799-78a24f50d2e3)
![pg2](https://github.com/user-attachments/assets/06ff9ab9-e2f6-4718-adf5-22cb418bdf3b)
![pg3](https://github.com/user-attachments/assets/771a199b-7207-4cc3-8252-6c66248368bd)

---

## Getting Started

### File Structure
```
Personal_Utility/
│
├── config/                        # Configuration files for models, prompts, and templates
│   ├── config.py                  # Loads and manages config.ini
│   ├── config.ini                 # Main configuration (options, LLMs, etc.)
│   ├── model.py                   # Model initialization (Groq, Ollama, etc.)
│   ├── resume_job_description.py  # Default job description for resume generation
│   ├── resume_template.py         # Default resume template
│   ├── variable_validation.py     # Pydantic/TypedDict validation for state and responses
│   └── prompts/                   # Prompt templates for LLM agents
│       ├── review_agent.py
│       ├── review_agent_to_create_resume.py
│       └── start_create_resume.py
│
├── LLMbackend/                    # Backend logic for LLM-powered features
│   ├── agents.py                  # Main agent logic for resume, feedback, etc.
│   ├── data_extraction.py         # File upload, parsing, and extraction logic
│   ├── llm.py                     # LLM orchestration and utility functions
│   ├── pdf_creator.py             # Markdown to PDF conversion
│   ├── pdf_oprations/             # PDF utilities (merging, preview, etc.)
│   │   └── merge.py
│   └── cv/                        # (Optional) Additional CV logic/modules
│       └── agno_cv.py
│
├── logger/                        # Logging utilities and logs
│   ├── logg_rep.py                # Logging setup and helpers
│   └── simple_tracker.log         # Main log file (gitignored)
│
├── ui/                            # Streamlit UI components
│   ├── app.py                     # Main Streamlit app entry point
│   └── sidebar.py                 # Sidebar logic and navigation
│
├── testing/                       # Test scripts and notebooks (gitignored)
│   ├── NoT Provided ❌
│
├── requirements.txt               # Python dependencies
├── .gitignore                     # Files/folders to ignore in git
└── README.md                      # Project overview and instructions
```
### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com/) (for local LLMs, if desired)
- [Groq API Key](https://console.groq.com/keys) (if using Groq)

### Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/Personal_Utility.git
   cd Personal_Utility
   ```

2. **Install dependencies:**
   ```pip install -r requirements.txt```

3. **Configure LLM Providers:**
    - Edit config/config.ini to set available models and options.
    - For Groq, obtain an API key.
    - Change your default JOB Description, Template Data.
        - Job Description
            - ```config\resume_job_description.py``` Add your 'Job Description' here
        - Template
            - ```config\resume_template.py``` Add your Default 'Template' details here

4. **Run the app:**
    ```streamlit run ui/app.py```

5. **Usage**
    - Select a utility from the sidebar: Resume Maker, PDF Merge, etc.
    - Upload your data (resume, job description, etc.) as prompted.
    - Interact with the LLM to generate, review, and improve your resume.
    - Download results as PDF.

6. **Troubleshooting 🚧**
    - Context Window?
        If you are using Groq free API Key, context window size is small. So kindly use OLLAMA.  
    - Missing fields in resume output?
        The app will prompt for missing information or leave placeholders.
    - Model connection issues?
        Ensure your API keys are correct and Ollama is running if using local models.
    - PDF conversion errors?
        Make sure wkhtmltopdf is installed and accessible if using pdfkit.