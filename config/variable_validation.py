from pydantic import BaseModel, Field
from typing import Annotated, Optional, Dict
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

class State(BaseModel):
    resume_input : Annotated[Optional[str], Field(description='Takes pre existing Resume to perform required adjustmemnts')] 
    text_input : Annotated[Optional[str], Field(description='Takes infomations which can be used as context for improving or creating a resume')]
    file_input : Annotated[Optional[str], Field(description='In addition to text_input, user can also add files as context')]
    session_id : Dict[str, str]
    

