from langchain_core.messages import SystemMessage, HumanMessage

from ..models.agent_state import AgentState, AgentStateUpdate
from ..models.deduplicated_claims import UniqueClaimsList
from ..settings.config import get_llm
from ..prompts.prompts import PromptsOrganizer
from ..tools.clustering import cluster_claims
import logging

logger = logging.getLogger(__name__)

def refiner_node(state: AgentState) -> AgentStateUpdate:
    """Refiner agent node, reducing raw claims to unique set, and giving a API flag for future tool usage"""

    raw_claims = state.get("raw_claims", [])
    logger.info(f"Deduplicator received {len(raw_claims)} raw claims")

    if not raw_claims:
        logger.warning("Refiner received empty list of claims. Skipping.")
        return {"unique_claims": []}

    claims_statements = [c.statement for c in raw_claims]
    claims_batches = cluster_claims(claims_statements)

    llm = get_llm("smart")
    structured_llm = llm.with_structured_output(UniqueClaimsList) # type: ignore
    all_unique_claims = []
    for i, batch in enumerate(claims_batches):
        try:
            claims_processed = "".join([f"{i} Claim: {c}\n" for i, c in enumerate(batch)])
            messages = [
                SystemMessage(content=PromptsOrganizer.REFINER_SYSTEM),
                HumanMessage(content=PromptsOrganizer.refiner_user(claims_processed))
            ]
            response = structured_llm.invoke(messages)
            
            if isinstance(response, UniqueClaimsList):
                all_unique_claims.extend(response.unique_claims) #type:ignore
                logger.info(f"Batch {i+1}/{len(claims_batches)} processed. Found {len(response.unique_claims)} unique items.") #type:ignore
            else:
                logger.warning(f"Batch {i+1} returned empty or invalid response.")
                
        except Exception as e:
            logger.error(f"Error in refiner_node: {e}")
            continue
    logger.info(f"Refiner finished. Reduced to {len(all_unique_claims)} unique claims")
    logger.info(f"\n\n{all_unique_claims}\n\n")
    return {"unique_claims": all_unique_claims}