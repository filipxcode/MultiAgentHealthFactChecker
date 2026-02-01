from langchain_core.messages import HumanMessage, SystemMessage

from ..models.research import ResearchQuery, ResearchInput
from ..settings.config import get_llm
from ..prompts.prompts import PromptsOrganizer
from ..tools.pubmed import research_simple

def reaserch_node(state: ResearchInput):
    
    llm = get_llm("fast")
    
    structured_llm = llm.with_structured_output(ResearchQuery)
    messages = [
        SystemMessage(content=PromptsOrganizer.RESEARCH_SYSTEM),
        HumanMessage(content=PromptsOrganizer.research_user(state.single_claim.statement))
    ]
    try:
        search_query_obj = structured_llm.invoke(messages)
        papers = research_simple(search_query_obj.search_query) # type:ignore
        return {"found_papers":papers}
    except Exception as e:
        print(e)
        return {"found_papers": None}