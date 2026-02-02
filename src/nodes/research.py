from langchain_core.messages import HumanMessage, SystemMessage

from ..models.research import ResearchQuery, ResearchState
from ..settings.config import get_llm
from ..prompts.prompts import PromptsOrganizer
from ..tools.pubmed import research_simple
import logging

logger = logging.getLogger(__name__)

def research_node(state: ResearchState):
    
    logger.info(f"Researching claim: {state.claim.statement[:50]}...")
    
    llm = get_llm("local")
    
    structured_llm = llm.with_structured_output(ResearchQuery)
    messages = [
        SystemMessage(content=PromptsOrganizer.RESEARCH_SYSTEM),
        HumanMessage(content=PromptsOrganizer.research_user(state.claim.statement))
    ]
    try:
        search_query_obj = structured_llm.invoke(messages)
        papers = research_simple(search_query_obj.search_query) # type:ignore
        logger.info(f"Found {len(papers)} papers for claim")
        return {"found_papers":papers}
    except Exception as e:
        logger.error(f"Error in research_node: {e}")
        return {"found_papers": []}