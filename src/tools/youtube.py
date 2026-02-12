import time
from langchain_community.document_loaders import YoutubeLoader
from langchain_core.documents import Document
import yt_dlp
import logging 
from ..settings.config import get_settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import random
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import http.cookiejar
import os
import json
from youtube_transcript_api.proxies import WebshareProxyConfig

logger = logging.getLogger(__name__)
"""Problem with this wrapper, yt is banning while too much request"
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
"""

def _load_from_cache(video_url: str) -> list[Document] | None:
    """Helper to check if transcript exists locally"""
    file_path = "files/transcriptions.jsonl"
    if not os.path.exists(file_path):
        return None
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("source") == video_url:
                        logger.info(f"Loaded transcript from cache for {video_url}")
                        return [Document(page_content=entry["text"], metadata={"source": video_url})]
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logger.warning(f"Error reading cache: {e}")
        
    return None

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception), 
    reraise=True
)
def youtube_transcribe(video_url: str, web_proxy: bool = False, save_transcript: bool = True, cached: bool = False) -> list[Document]:
    """
    Custom implementation of yt transcription, avoiding YT IP ban.
    """
    if cached:
        cached_docs = _load_from_cache(video_url)
        if cached_docs:
            return cached_docs

    sleep_time = random.uniform(1.5, 4.0) 
    time.sleep(sleep_time)

    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    else:
        video_id = video_url.split("/")[-1]
    
    if web_proxy:
        yt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username="<proxy-username>",
                proxy_password="<proxy-password>",
            )
        )
    else:
        yt_api = YouTubeTranscriptApi()
        
    transcript_list_obj = yt_api.list(video_id)

    try:
        transcript = transcript_list_obj.find_transcript(['en', 'pl'])
    except Exception:
        try: 
            transcript = transcript_list_obj.find_generated_transcript(['en'])
        except:
            transcript = next(iter(transcript_list_obj))
    data = transcript.fetch()
    full_text = " ".join([item.text for item in data])
    final_text = full_text.replace("\n", " ")
    result = [Document(page_content=final_text, metadata={"source": video_url})]

    if save_transcript:
        data_entry = {
            "source": video_url,
            "text": final_text,
        }

        os.makedirs("files", exist_ok=True)
        with open("files/transcriptions.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(data_entry, ensure_ascii=False) + "\n")
    return result

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception), 
    reraise=True
)
def get_video_duration(url: str, cookies_file: str = "cookies.txt") -> dict:
    """
    Retrieves video duration using yt-dlp WITH COOKIES.
    """
    sleep_time = random.uniform(1.5, 4.0) 
    time.sleep(sleep_time)
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'simulate': True,
        'skip_download': True,
        'nocheckcertificate': True,
    }

    if os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file

    settings = get_settings()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        if not info:
            return {"error": "Failed to extract video information (info is None)."}
        
        duration = info.get('duration')
        
        if duration is None:
            return {"error": "Video found, but duration data is missing."}
        
        if duration > settings.MAX_VIDEO_DURATION_SEC:
            msg = f"Film is too long ({duration}s). Limit {settings.MAX_VIDEO_DURATION_SEC}s."
            logger.warning(msg)
            return {"error": msg}
        
        return {"duration": int(duration)}