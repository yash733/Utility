from pydantic import BaseModel, Field
from typing import Annotated, Optional, Dict, TypedDict, Literal
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

class State(TypedDict):
    resume : str
    user_request : str
    user_suggestion : str
    final_resume : str
    suggestion : str
    sentiment : Literal['Perfect', 'Improvement Required']

class response_analysis(BaseModel):
    sentiment : Literal['Perfect', 'Improvement Required'] = Field(..., description='If the user is satisfied with the result pass Perfect else pass Improvement Required to make required changes')

class expert_review_resume(BaseModel):
    sentiment : Literal['Perfect', 'Improvement Required'] = Field(..., description='If review agent thinks some sort of improvement is required then it will pass "Improvement Required" if all is at perfection ir will pass "Perfect"')
    suggestion : Optional[str] = Field(description=f'If "sentiment" == "Improvement Required", then provide detailed instruction and areas of improvement required to improve resume impact increasing selection chances.')
    resume : Optional[str] = Field(description=f'If "sentiment" == "Perfect" then provide the final tailored resume.')