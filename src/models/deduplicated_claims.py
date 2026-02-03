from pydantic import BaseModel, Field
from typing import Literal
class UniqueClaim(BaseModel):
    """Claim model with additional router flag for API usage"""
    topic: str = Field(description="Short topic, e.g. 'Cardiology'")
    statement: str = Field(description="The refined, scientific statement.")
    quote_verbatim: str = Field(description="Original quote (or merged quotes).")
    
    verification_tool: Literal["PUBMED", "TAVILY"] = Field(
        description="The tool assigned to verify this claim."
    )
    
class UniqueClaimsList(BaseModel):
    """
    Final deduplicated list of claims
    """
    unique_claims: list[UniqueClaim] | None = Field(
        description="List of unique claims after duplicate removal. If claim A and B say the same thing, merge them into one, better formulated claim."
    )