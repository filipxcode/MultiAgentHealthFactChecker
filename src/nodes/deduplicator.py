from langchain_core.messages import SystemMessage, HumanMessage

from ..models.agent_state import AgentState
from ..models.deduplicated_claims import UniqueClaimsList
from ..settings.config import get_llm
from ..prompts.prompts import PromptsOrganizer

def deduplicator_node(state: AgentState):
    """Deduplicator agent node, reducing raw claims to unique set"""
    
    #HARD LIMIT FOR TESTS
    claims_limited = state.raw_claims[:5]
    
    claims_processed = ",".join([f"{i} Claim: {c}\n" for i, c in enumerate(claims_limited)])
    
    llm = get_llm("smart")
    
    structured_llm = llm.with_structured_output(UniqueClaimsList)
    
    messages = [
        SystemMessage(content=PromptsOrganizer.DEDUPLICATOR_SYSTEM),
        HumanMessage(content=PromptsOrganizer.deduplicate_user(claims_processed))
    ]
    
    try:
        response = structured_llm.invoke(messages)
        
        if isinstance(response, UniqueClaimsList):
            final_claims = response.unique_claims or []
        else:
            final_claims = []
            
        return {"unique_claims": final_claims}

    except Exception as e:
        print(f"Error in deduplicator_node: {e}")
        return {"unique_claims": []} 