from tavily import TavilyClient
from ..settings.config import get_settings
from ..models.research import ScientificPaper
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception)
)
def research_pubmed(claim: str):
    settings=get_settings()
    tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
    results = []
    try:
        response = tavily.search(
        query=claim,
        search_depth="basic",
        include_domains=["pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov"],
        max_results=5
        )
        for result in response['results']:
            results.append(ScientificPaper(content=result['content'], url=result['url']))
        return results
    except Exception as e:
        raise TimeoutError(f"Error to connect tavily {e}")