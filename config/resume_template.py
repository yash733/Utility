import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

def default():
    template = '''
            # [Your Full Name]

            **[Your Phone Number] | [Your Email Address] | [LinkedIn Profile URL] | [City, State/Country]**

            ---

            ## Professional Summary
            *Write a compelling 2-3 sentence summary highlighting your key qualifications, years of experience, and career objectives. Focus on what value you bring to potential employers.*

            ---

            ## Work Experience

            ### [Job Title]
            **[Company Name] | [City, State] | [Start Date] - [End Date]**
            - Accomplished [specific achievement with quantifiable results]
            - Led/managed [specific responsibility that demonstrates leadership or expertise]
            - Improved/increased [another achievement with measurable impact]
            - Collaborated with [description of teamwork or cross-functional work]

            ### [Previous Job Title]
            **[Company Name] | [City, State] | [Start Date] - [End Date]**
            - [Key accomplishment with specific metrics/results]
            - [Another significant responsibility or achievement]
            - [Additional relevant experience point]

            ### [Earlier Position (if relevant)]
            **[Company Name] | [City, State] | [Start Date] - [End Date]**
            - [Brief description of key responsibilities and achievements]

            ---

            ## Education

            ### [Degree Type and Major]
            **[University/College Name] | [City, State] | [Graduation Year]**
            - GPA: [Include if 3.5 or higher]
            - Relevant Coursework: [List 3-5 relevant courses]
            - Honors/Awards: [Dean's List, scholarships, etc.]

            ---

            ## Skills

            **Technical Skills:** [Programming languages, software, tools, platforms]
            **Industry Knowledge:** [Specific expertise areas, methodologies, frameworks]
            **Languages:** [Language and proficiency level]
            **Soft Skills:** [Leadership, communication, problem-solving, etc.]

            ---

            ## Projects

            ### [Project Name]
            **[Technologies Used] | [Date/Duration]**
            - [Brief description of the project and your role]
            - [Key outcomes, metrics, or impact achieved]
            - [Link to project if available: github.com/username/project]

            ### [Another Project Name]
            **[Technologies Used] | [Date/Duration]**
            - [Project description and your contributions]
            - [Results or learning outcomes]

            ---

            ## Certifications

            - **[Certification Name]** - [Issuing Organization] | [Date Earned]
            - **[Another Certification]** - [Issuing Organization] | [Date Earned]

            ---

            ## Additional Sections *(Include as relevant)*

            ### Publications
            - [Publication Title], [Journal/Conference Name], [Date]
            - [Another Publication], [Venue], [Date]

            ### Awards & Recognition
            - [Award Name] - [Awarding Organization] | [Date]
            - [Recognition] - [Details] | [Date]

            ### Volunteer Experience
            - **[Role]** - [Organization Name] | [Dates]
            - [Brief description of contributions and impact]

            ### Professional Memberships
            - [Organization Name] - [Membership Type] | [Dates]

            ---

            ## Tips for Using This Template:

            1. **Customize for each application** - Tailor content to match job requirements
            2. **Use action verbs** - Start bullet points with strong verbs (achieved, led, developed, etc.)
            3. **Quantify achievements** - Include numbers, percentages, and specific results whenever possible
            4. **Keep it concise** - Aim for 1-2 pages depending on experience level
            5. **Use consistent formatting** - Maintain uniform fonts, spacing, and bullet styles
            6. **Proofread carefully** - Check for spelling, grammar, and formatting errors
            7. **Save as PDF** - Preserve formatting when submitting electronically
                '''
    return template