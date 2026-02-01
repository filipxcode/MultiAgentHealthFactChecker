from langchain_core.messages import SystemMessage, HumanMessage

from ..models.extractor import ExtractorInput, ExtractorResult
from ..settings.config import get_llm
from ..prompts.prompts import PromptsOrganizer

def extractor_node(state: ExtractorInput):
    """Extractor agent node, handling single chunk"""
    chunk = state.current_chunk_text
    
    llm = get_llm("fast")
    
    structured_llm = llm.with_structured_output(ExtractorResult)
    
    messages = [
        SystemMessage(content=PromptsOrganizer.EXTRACTOR_SYSTEM),
        HumanMessage(content=PromptsOrganizer.extractor_user(chunk))
    ]
    
    try:
        response = structured_llm.invoke(messages)
        
        if isinstance(response, ExtractorResult):
            safe_claims = response.found_claims or []
        else:
            safe_claims = []
            
        return {"raw_claims": safe_claims}
    except Exception as e:
        print(f"Error in extractor_node: {e}")
        return {"raw_claims": []}