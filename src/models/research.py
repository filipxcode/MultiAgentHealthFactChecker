from pydantic import Field, BaseModel
from ..models.judge import VerificationResult
from ..models.deduplicated_claims import UniqueClaim

class ResearchInput(BaseModel):
    """Helper input for single claim to research"""
    single_claim: UniqueClaim

class ResearchQuery(BaseModel):
    """LLM research structured query"""
    search_query: str = Field(
        description="The final optimized keyword string ready for search engine."
    )
    

class ScientificPaper(BaseModel):
    """Single fact found in DB"""
    content: str
    url: str | None
    

class ResearchState(BaseModel):
    """Single research state for each subgraph"""
    claim: UniqueClaim

    found_papers: list[ScientificPaper] = Field(default_factory=list)
    
    final_verdicts: list[VerificationResult] = Field(default_factory=list)