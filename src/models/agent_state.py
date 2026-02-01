import operator
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field

from .claim import Claim  #
from .judge import VerificationResult

class AgentState(BaseModel):
    """
    Global state handler
    """
    
    video_url: str = Field(description="Link do filmu YouTube (od usera)")
    
    transcript_chunks: list[str] | None = Field(default=None) 
    
    raw_claims: Annotated[list[Claim], operator.add] = Field(default_factory=list)
    
    unique_claims: list[Claim] = Field(default_factory=list)
    
    final_verdicts: Annotated[list[VerificationResult], operator.add] = Field(default_factory=list)