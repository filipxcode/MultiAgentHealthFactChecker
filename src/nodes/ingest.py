from ..tools.chunker import chunk_text
from ..tools.youtube import youtube_transcribe
from ..models.agent_state import AgentState

def ingest_node(state: AgentState):
    """None LLM node, handling chunking and transcription"""
    data = youtube_transcribe(state.video_url)
    chunked_data = chunk_text(data, 2000, 200)
    transcript_chunks = [str(c.page_content) for c in chunked_data]
    return {"transcript_chunks":transcript_chunks}