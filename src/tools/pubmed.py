from langchain_community.retrievers import PubMedRetriever
from ..settings.config import get_settings
from ..models.research import ScientificPaper

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
