from langchain_core.messages import HumanMessage, SystemMessage

from ..models.research import ResearchState
from ..models.judge import VerificationResult
from ..prompts.prompts import PromptsOrganizer
from ..settings.config import get_llm

def judge_node(state: ResearchState):
    papers = state.found_papers
    claim = state.claim.statement
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
    llm = get_llm("smart")
    llm_structured = llm.with_structured_output(VerificationResult)
    try:
        response = llm_structured.invoke(messages)
        response.sources = source_list_for_report #type:ignore
        return {"final_verdicts": [response]}
    except Exception as e:
        print(f"Judge Error: {e}")
        return {"final_verdicts": []}