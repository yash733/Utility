from pydantic import BaseModel, Field
from typing import Annotated, Optional, Dict, TypedDict
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

class State(TypedDict):
    resume : str
    user_request : str
    final_resume : str