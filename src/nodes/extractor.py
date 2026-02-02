from langchain_core.messages import SystemMessage, HumanMessage

from ..models.extractor import ExtractorInput, ExtractorResult
from ..settings.config import get_llm
from ..prompts.prompts import PromptsOrganizer
import logging

logger = logging.getLogger(__name__)

def extractor_node(state: ExtractorInput):
    """Extractor agent node, handling single chunk"""
    if isinstance(state, dict):
        chunk = state.get("current_chunk_text", "")
    else:
        chunk = state.current_chunk_text
        
    logger.info(f"Extractor processing chunk of length {len(chunk)}")
    
    llm = get_llm("local")
    
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
            
        logger.info(f"Extractor found {len(safe_claims)} claims")
        logger.info(f"\n\nCLAIM {safe_claims} claims\n\n")
        return {"raw_claims": safe_claims}
    except Exception as e:
        logger.error(f"Error in extractor_node: {e}")
        return {"raw_claims": []}