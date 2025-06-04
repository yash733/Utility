import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

def default():
    template = '''
                Full Name
                Contact Information: [Phone] | [Email] | [LinkedIn] | [Location]

                Professional Summary:
                A concise summary of qualifications and career goals.

                Work Experience:
                - Job Title, Company, Location, Dates
                • Key achievement or responsibility
                • Key achievement or responsibility

                Education:
                - Degree, Institution, Location, Dates
                • Relevant coursework or honors

                Skills:
                - Skill 1, Skill 2, Skill 3, ...

                Projects:
                - Project Title
                • Brief description and impact

                Certifications (if any):
                - Certification Name, Issuer, Date

                Additional Sections (if relevant):
                - Publications, Awards, Languages, Volunteer Experience, etc.
                '''
    return template