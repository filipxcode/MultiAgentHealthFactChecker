from pydantic import BaseModel, Field
from typing import Literal
from ..models.deduplicated_claims import UniqueClaim

class JudgeOutput(BaseModel):
    """
    Structure for the LLM output (without the Claim object).
    """
    verdict: Literal["True", "False", "Unverified", "Nuanced"] = Field(
        description="Categorical assessment: True (confirmed), False (debunked), Unverified (no enough evidence), Nuanced (partially true/context dependent)."
    )
    
    confidence_score: int = Field(
        description="Confidence score (0-100). High (80-100) for meta-analyses/RCTs, Low (0-40) for observational studies or lack of direct evidence."
    )
    
    explanation: str = Field(
        description="Short, accessible justification of the verdict in ENGLISH. Describe what the studies say and why the assessment is what it is."
    )

class VerificationResult(JudgeOutput):
    """
    Final result including the Claim object (for internal use).
    """
    claim: UniqueClaim
    
    sources: list[str] = Field(
        default_factory=list,
        description="List of links to scientific sources used in verification."
    )
