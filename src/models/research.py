from pydantic import Field, BaseModel
from ..models.claim import Claim
from ..models.judge import VerificationResult

class ResearchInput(BaseModel):
    single_claim: Claim
    
class ResearchQuery(BaseModel):
    search_query: str = Field(
        description="Precise scientific search query in English. Translate Polish concepts into English medical terminology (MeSH terms if possible)."
    )
    

class ScientificPaper(BaseModel):
    """Single fact found in DB"""
    content: str
    url: str | None
    

class ResearchState(BaseModel):
    claim: Claim

    found_papers: list[ScientificPaper] = Field(default_factory=list)
    
    final_verdict: VerificationResult | None = None