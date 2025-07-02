from pydantic import BaseModel, Field
from typing import Literal

class NumericVote(BaseModel):
    """
    Defines the schema for an individual vote response.
    The vote must be either 1 or 2.
    """
    vote: Literal[1, 2] = Field(description="The vote must be 1 or 2")