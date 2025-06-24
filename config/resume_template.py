import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

def default():
    template = """    
    # [FULL_NAME]

    **Contact:** [PHONE] | [EMAIL] | [LINKEDIN] | [GITHUB] | [PORTFOLIO]  
    **Location:** [LOCATION]

    ---

    ## Professional Summary
    [A concise 2-3 sentence summary highlighting key qualifications, years of experience, and career focus - to be customized based on context]

    ---

    ## Work Experience

    **[Job Title]** | **[Company Name]** | **[Location]** | **[Start Date - End Date]**
    - [Achievement-focused bullet point with quantifiable results]
    - [Key responsibility that demonstrates relevant skills]
    - [Impact or improvement made in the role]

    **[Job Title]** | **[Company Name]** | **[Location]** | **[Start Date - End Date]**
    - [Achievement-focused bullet point with quantifiable results]
    - [Key responsibility that demonstrates relevant skills]
    - [Impact or improvement made in the role]

    ---

    ## Education

    **[Degree]** | **[Institution Name]** | **[Location]** | **[Graduation Date]**
    - [Relevant coursework, honors, GPA if > 3.5, or notable achievements]

    ---

    ## Technical Skills

    - **Programming Languages:** [Language1, Language2, Language3]
    - **Frameworks & Technologies:** [Framework1, Framework2, Framework3]
    - **Tools & Platforms:** [Tool1, Tool2, Tool3]
    - **Databases:** [Database1, Database2]
    - **Other:** [Additional relevant skills]

    ---

    ## Projects

    **[Project Name]** | **[Technology Stack]** | **[Date]** | [Project Link](project_url)
    - [Brief description of project purpose and your role]
    - [Key technical challenges solved or features implemented]
    - [Quantifiable impact or results if applicable]

    **[Project Name]** | **[Technology Stack]** | **[Date]** | [Project Link](project_url)
    - [Brief description of project purpose and your role]
    - [Key technical challenges solved or features implemented]
    - [Quantifiable impact or results if applicable]

    ---

    ## Certifications
    - **[Certification Name]** | **[Issuing Organization]** | **[Date]**
    - **[Certification Name]** | **[Issuing Organization]** | **[Date]**

    ---

    ## Additional Information
    - **Languages:** [Language1 (Proficiency), Language2 (Proficiency)]
    - **Awards:** [Award Name, Year]
    - **Publications:** [Publication Title, Year] (if applicable)
    - **Volunteer Experience:** [Organization, Role, Year] (if applicable)"""
    
    return template