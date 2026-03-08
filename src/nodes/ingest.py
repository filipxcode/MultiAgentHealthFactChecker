from ..tools.chunker import chunk_text
from ..tools.youtube import youtube_transcribe, get_video_duration
from ..models.agent_state import AgentState, AgentStateUpdate

import logging
logger = logging.getLogger(__name__)

def ingest_node(state: AgentState) -> AgentStateUpdate:
    """None LLM node, handling chunking and transcription"""
    video_url = state["video_url"]
    logger.info(f"Starting ingestion for video: {video_url}")
    video_info = get_video_duration(video_url)
    if "error" in video_info:
        logger.error(f"Ingest failed: {video_info['error']}")
        return {"errors": video_info['error']}
    
    data = youtube_transcribe(video_url)
    if data:
        total_len = sum(len(d.page_content) for d in data)
        logger.info(f"Retrieved transcript length: {total_len} chars")
        chunked_data = chunk_text(data, 2000, 200)
        transcript_chunks = [str(c.page_content) for c in chunked_data]
        logger.info(f"Created {len(transcript_chunks)} chunks")
        return {"transcript_chunks":transcript_chunks}
    
    return {"errors": "Video not found"}