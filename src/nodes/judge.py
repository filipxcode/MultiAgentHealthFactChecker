from langchain_core.messages import HumanMessage, SystemMessage

from ..models.research import ResearchState
from ..models.judge import VerificationResult
from ..prompts.prompts import PromptsOrganizer
from ..settings.config import get_llm
import logging

logger = logging.getLogger(__name__)

def judge_node(state: ResearchState):
    """Judge node, used for taking claims and sources from single sub-state and converting it to coherent content"""
    papers = state.found_papers
    claim = state.claim.statement
    logger.info(f"Judging claim: {claim[:50]}... with {len(papers or [])} papers")
    evidence_text = ""
    source_list_for_report = []
    for i, p in enumerate(papers):
        evidence_text += f"--- PAPER {i+1} ---\nUrl: {p.url}\nContent: {p.content}\n\n"
        source_string = f"({p.url})"
        source_list_for_report.append(source_string)
    
    messages=[
        SystemMessage(content=PromptsOrganizer.JUDGE_SYSTEM),
        HumanMessage(content=PromptsOrganizer.judge_user(claim=claim, evidence=evidence_text))
    ]
    llm = get_llm("local")
    llm_structured = llm.with_structured_output(VerificationResult)
    try:
        response = llm_structured.invoke(messages)
        response.sources = source_list_for_report #type:ignore
        logger.info(f"Verdict for claim: {response.verdict}")  #type:ignore
        return {"final_verdicts": [response]}
    except Exception as e:
        logger.error(f"Judge Error: {e}")
        return {"final_verdicts": []}