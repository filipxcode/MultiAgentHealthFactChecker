from pydantic import BaseModel, Field
from typing import Literal

class VerificationResult(BaseModel):
    """
    """
    verdict: Literal["True", "False", "Unverified", "Nuanced"] = Field(
        description="Categorical assessment: True (confirmed), False (debunked), Unverified (no enough evidence), Nuanced (partially true/context dependent)."
    )
    
    confidence_score: int = Field(
        description="Confidence score (0-100). High (80-100) for meta-analyses/RCTs, Low (0-40) for observational studies or lack of direct evidence."
    )
    
    explanation_pl: str = Field(
        description="Krótkie, przystępne uzasadnienie werdyktu w języku POLSKIM. Opisz, co mówią badania i dlaczego ocena jest taka, a nie inna."
    )
    
    sources: list[str] = Field(
        default_factory=list,
        description="Lista linków do źródeł naukowych użytych w weryfikacji."
    )