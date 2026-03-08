import operator
from typing import Annotated, TypedDict

from .claim import Claim  #
from .judge import VerificationResult
from .deduplicated_claims import UniqueClaim


class AgentState(TypedDict, total=False):
    """
    Global state handler
    """

    video_url: str
    transcript_chunks: list[str] | None
    raw_claims: Annotated[list[Claim], operator.add]
    unique_claims: list[UniqueClaim]
    gatekeeper_verdict: str
    final_verdicts: Annotated[list[VerificationResult], operator.add]
    final_report: str
    errors: str | None


class AgentStateUpdate(TypedDict, total=False):
    """Partial state update returned by nodes."""

    transcript_chunks: list[str] | None
    raw_claims: Annotated[list[Claim], operator.add]
    unique_claims: list[UniqueClaim]
    gatekeeper_verdict: str
    final_verdicts: Annotated[list[VerificationResult], operator.add]
    final_report: str
    errors: str | None