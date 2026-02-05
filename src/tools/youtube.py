import time
from langchain_community.document_loaders import YoutubeLoader
from langchain_core.documents import Document
import yt_dlp
import logging 

logger = logging.getLogger(__name__)

def youtube_transcribe(url: str) -> list[Document]:
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            loader = YoutubeLoader.from_youtube_url(
                url, 
                language=["pl", "en"]
            )
            return loader.load()
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise TimeoutError(f"Youtube transcribe error: {str(e)}")
            time.sleep(1 + attempt) 
    return []


def get_video_duration(url: str) -> dict:
    """
    Retrieves video duration using yt-dlp.
    Returns: dict with {"duration": int} on success OR {"error": str} on failure.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'simulate': True,
        'skip_download': True,
        'nocheckcertificate': True, 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: # type: ignore
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return {"error": "Failed to extract video information (info is None)."}
            
            duration = info.get('duration')
            
            if duration is None:
                logger.warning(f"Could not determine duration for: {url}")
                return {"error": "Video found, but duration data is missing."}
                
            return {"duration": int(duration)}

    except Exception as e:
        error_msg = f"yt-dlp DownloadError (Geo-block/Private/Unavailable): {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
        