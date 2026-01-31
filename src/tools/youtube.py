import time
from langchain_community.document_loaders import YoutubeLoader
from langchain_core.documents import Document

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