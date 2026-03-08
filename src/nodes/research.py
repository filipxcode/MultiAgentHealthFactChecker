from langchain_core.messages import HumanMessage, SystemMessage
from ..models.research import ResearchQuery, ResearchState
from typing import Literal
from ..models.research import ResearchStateUpdate
from ..settings.config import get_llm
from ..prompts.prompts import PromptsOrganizer
from ..tools.pubmed import research_pubmed
from ..tools.tavily import research_tavily
import logging

logger = logging.getLogger(__name__)

def research_node(state: ResearchState) -> ResearchStateUpdate:
    """
    Research node handling single distributed claim with Auto-Fallback.
    """
    claim = state["claim"]
    logger.info(f"Researching claim: {claim.statement[:50]}...")
    
    try:
        llm = get_llm("fast")
        structured_llm = llm.with_structured_output(ResearchQuery)
        
        messages = [
            SystemMessage(content=PromptsOrganizer.RESEARCH_SYSTEM),
            HumanMessage(content=PromptsOrganizer.research_user(claim.statement))
        ]
        
        search_query_obj = structured_llm.invoke(messages)
        query = search_query_obj.search_query #type:ignore
        tool = claim.verification_tool
        
        papers = []

        if tool == "PUBMED":
            papers = research_pubmed(query)
            
            if papers:
                logger.info(f"Found {len(papers)} papers via PubMed")
            else:
                logger.warning(f"PubMed found 0 papers. Fallback to Tavily General for: '{query}'")
                papers = research_tavily(query)
                logger.info(f"Found {len(papers)} papers via Tavily Fallback")
                
        elif tool == "TAVILY":
            papers = research_tavily(query)
            logger.info(f"Found {len(papers)} papers via Tavily")
            
        else:
            logger.error(f" Unknown verification tool: {tool}")
            papers = []

        return {"found_papers": papers}

    except Exception as e:
        logger.error(f"🔥 Error in research_node: {e}")
        return {"found_papers": []}

def route_research_output(state: ResearchState) -> Literal["continue", "stop"]:
    """
    Router for research, if papers not found, stop.
    """
    papers = state.get("found_papers", [])
    if papers and len(papers) > 0:
        return "continue"
    return "stop"