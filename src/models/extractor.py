from pydantic import BaseModel, Field
from .claim import Claim
class ExtractorInput(BaseModel):
    """Single input for extract agent"""
    current_chunk_text: str
    
class ExtractorResult(BaseModel):
    """Output for extract agent"""
    found_claims: list[Claim] | None = Field(
        description="List of all medical/scientific claims found in this text chunk. If none found, return an empty list."
    )
    has_medical_content: bool = Field(
        description="Helper flag. True if any medical statements were made in the chunk."
    )