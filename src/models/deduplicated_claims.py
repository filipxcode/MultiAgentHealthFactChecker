from pydantic import BaseModel, Field
from .claim import Claim

class UniqueClaimsList(BaseModel):
    """
    Final deduplicated list of claims
    """
    unique_claims: list[Claim] | None = Field(
        description="List of unique claims after duplicate removal. If claim A and B say the same thing, merge them into one, better formulated claim."
    )