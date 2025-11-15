from pydantic import BaseModel
from typing import List

class StatesResponse(BaseModel):
    """
    Defines the response model for a list of states.
    """
    states: List[str]
