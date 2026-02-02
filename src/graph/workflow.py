from langgraph.graph import StateGraph, END, START
from ..models.agent_state import AgentState
from ..models.research import ResearchState
from langgraph.types import Send
from ..nodes.deduplicator import deduplicator_node
from ..nodes.extractor import extractor_node
from ..nodes.ingest import ingest_node
from ..nodes.research import research_node
from ..nodes.judge import judge_node
from ..nodes.reporter import reporter_node
from ..nodes.gatekeeper import gatekeeper_node

import logging

logger = logging.getLogger(__name__)

class Workflow:
    def __init__(self):
        logger.info("Initializing Workflow graph")
        self.builed_subgraph = self._build_subgraph()
        self.main_graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("ingest", ingest_node)
        graph.add_node("gatekeeper", gatekeeper_node)
        graph.add_node("extractor", extractor_node)
        graph.add_node("deduplicator", deduplicator_node)
        graph.add_node("subgraph", self.builed_subgraph)
        graph.add_node("reporter", reporter_node)
        graph.set_entry_point("ingest")
        graph.add_edge("ingest", "gatekeeper")
        graph.add_conditional_edges(
            "gatekeeper",
            self._route_gatekeeper,
            ["extractor", END]
        )
        graph.add_edge("extractor", "deduplicator")
        graph.add_conditional_edges("deduplicator", 
            self._distribute_research,
            ["subgraph"])
        graph.add_edge("subgraph", "reporter")
        graph.add_edge("reporter", END)
        return graph.compile()
    
    def _build_subgraph(self):
        subgraph = StateGraph(ResearchState)
        subgraph.add_node("research", research_node)
        subgraph.add_node("judge", judge_node)
        subgraph.add_edge(START, "research")
        subgraph.add_edge("research", "judge")
        subgraph.add_edge("judge", END)
        return subgraph.compile()
    
    def _distribute_chunks(self, state):
        """Distributing chunks for each extract agent"""
        chunks = state.transcript_chunks or []
        return [
            Send("extractor", {"current_chunk_text": chunk}) 
            for chunk in chunks
        ]
    
    def _distribute_research(self, state):
        deduplicated_claims = state.unique_claims
        return [
            Send("subgraph", {"claim": claim}) 
            for claim in deduplicated_claims
        ]
    
    def _route_gatekeeper(self, state):
        verdict = state.gatekeeper_verdict
        if verdict == "pass":
            return self._distribute_chunks(state)
        else:
            return END

    def run(self, video_url: str):
        logger.info(f"Starting workflow run for url: {video_url}")
        initial_state = AgentState(video_url=video_url)
        final_state = self.main_graph.invoke(initial_state)
        return final_state