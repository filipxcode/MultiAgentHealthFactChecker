from langchain_core.messages import HumanMessage, SystemMessage

from ..models.research import ResearchState, ResearchStateUpdate
from ..models.judge import VerificationResult, JudgeOutput
from ..prompts.prompts import PromptsOrganizer
from ..settings.config import get_llm
import logging

logger = logging.getLogger(__name__)

def judge_node(state: ResearchState) -> ResearchStateUpdate:
    """Judge node, used for taking claims and sources from single sub-state and converting it to coherent content"""
    papers = state.get("found_papers", [])
    claim = state["claim"]
    claim_text = claim.statement
    logger.info(f"Judging claim: {claim_text[:50]}... with {len(papers or [])} papers")
    evidence_text = ""
    source_list_for_report = []
    for i, p in enumerate(papers):
        evidence_text += f"--- PAPER {i+1} ---\nUrl: {p.url}\nContent: {p.content}\n\n"
        source_string = f"({p.url})"
        source_list_for_report.append(source_string)
    
    messages=[
        SystemMessage(content=PromptsOrganizer.JUDGE_SYSTEM),
        HumanMessage(content=PromptsOrganizer.judge_user(claim=claim_text, evidence=evidence_text, topic=claim.topic))
    ]
    llm = get_llm("fast")
    llm_structured = llm.with_structured_output(JudgeOutput) #type:ignore
    
    try:
        response = llm_structured.invoke(messages)
        
        if isinstance(response, JudgeOutput):
            final_result = VerificationResult(
                claim=claim,
                verdict=response.verdict,
                confidence_score=response.confidence_score,
                explanation=response.explanation,
                sources=source_list_for_report
            )
            logger.info(f"Verdict for claim: {final_result.verdict}")
            return {"final_verdicts": [final_result]}
        else:
            logger.warning("Judge returned invalid response format")
            return {"final_verdicts": []}
            
    except Exception as e:
        logger.error(f"Judge Error: {e}")
        return {"final_verdicts": []}
