from langchain_community.retrievers import PubMedRetriever
from ..settings.config import get_settings
from ..models.research import ScientificPaper
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception) 
)
def research_simple(query: str) -> list[ScientificPaper]:
    settings = get_settings()
    retriever = PubMedRetriever(email=settings.PUBMED_EMAIL) # type: ignore
    docs = retriever.invoke(query)
    results = []
    for d in docs:
        pmid = d.metadata.get('uid')
        
        link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "Brak linku"
        
        results.append(ScientificPaper(content=d.page_content, url=link))
    return results
