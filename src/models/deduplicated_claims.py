from pydantic import BaseModel, Field
from .claim import Claim

class UniqueClaimsList(BaseModel):
    """
    Final deduplicated list of claims
    """
    unique_claims: list[Claim] | None = Field(
        description="Lista unikalnych tez po usunięciu duplikatów. Jeśli teza A i B mówią to samo, połącz je w jedną, lepiej sformułowaną."
    )