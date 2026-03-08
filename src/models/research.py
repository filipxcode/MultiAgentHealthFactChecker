from pydantic import Field, BaseModel
from typing import TypedDict
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
    

class ResearchState(TypedDict, total=False):
    """Single research state for each subgraph"""
    claim: UniqueClaim

    found_papers: list[ScientificPaper]
    final_verdicts: list[VerificationResult]


class ResearchStateUpdate(TypedDict, total=False):
    """Partial research state update returned by subgraph nodes."""

    found_papers: list[ScientificPaper]
    final_verdicts: list[VerificationResult]