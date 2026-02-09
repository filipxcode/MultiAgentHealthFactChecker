from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from pydantic import SecretStr
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router import SemanticRouter 
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering

class Settings(BaseSettings):
    GROQ_API_KEY: str = Field(default="")
    MODEL_FAST: str = "llama-3.1-8b-instant"
    MODEL_SMART: str = "llama-3.3-70b-versatile"
    MODEL_LOCAL: str = "llama3.1"
    EMBEDDING_MODEL_ROUTER: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_CHUNK_SIZE_ROUTER: int = 350
    TEMPERATURE: float = 0.0
    CHUNK_SIZE: int = 10000 
    CHUNK_OVERLAP: int = 500
    PUBMED_API_KEY: str = Field(default="")
    PUBMED_EMAIL: str = Field(default="unknown@example.com")
    TAVILY_API_KEY: str = Field(default="")
    EMBEDDING_MODEL_CLUSTERING: str = "sentence-transformers/all-mpnet-base-v2"
    CLUSTERING_DISTANCE_THRESHOLD: float = 0.75
    CLUSTERING_LINKAGE: str = "average"
    CLUSTERING_METRIC: str = "cosine"
    CLUSTERING_MIN_CLAIMS: int = 15
    MAX_BATCH_SIZE: int = 25
    MAX_VIDEO_DURATION_SEC: int = 3600
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore" 
    )
        
@lru_cache()
def get_settings() -> Settings:
    return Settings()

class LLMFactory:
    @staticmethod
    @lru_cache(maxsize=1)
    def get_smart_llm(temperature: float = 0.0):
        settings = get_settings()
        
        base_llm = ChatGroq(
            model=settings.MODEL_SMART,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=temperature,
            max_retries=3,
        )
        return base_llm

    @staticmethod
    @lru_cache(maxsize=1)
    def get_fast_llm(temperature: float = 0.0):
        settings = get_settings()
        
        base_llm = ChatGroq(
            model=settings.MODEL_FAST,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=temperature,
            max_retries=3,
        )
        return base_llm

    @staticmethod
    @lru_cache(maxsize=1)
    def get_local_llm(temperature: float = 0.0):
        settings = get_settings()
        return ChatOllama(
            model=settings.MODEL_LOCAL,
            temperature=temperature
        )


    @staticmethod
    @lru_cache(maxsize=1)
    def get_router_encoder():
        settings = get_settings()
        return HuggingFaceEncoder(name=settings.EMBEDDING_MODEL_ROUTER)

    @staticmethod
    def get_semantic_router(routes: list):
        """Builds and returns a SemanticRouter instance (No caching here due to unhashable routes)"""
        sr = SemanticRouter(encoder=LLMFactory.get_router_encoder()) 
        if routes:
            sr.add(routes) 
        return sr
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_cluster_encoder():
        settings = get_settings()
        return SentenceTransformer(settings.EMBEDDING_MODEL_CLUSTERING)
    
    @staticmethod
    def get_clustering_model():
        """Returns a configured AgglomerativeClustering instance. NOT CACHED as it holds state after fitting."""
        settings = get_settings()
        return AgglomerativeClustering(
            n_clusters=None, 
            distance_threshold=settings.CLUSTERING_DISTANCE_THRESHOLD, 
            metric=settings.CLUSTERING_METRIC, 
            linkage=settings.CLUSTERING_LINKAGE #type: ignore
        )
    
def get_llm(type: str = "local"):
    if type == "smart":
        return LLMFactory.get_smart_llm()
    elif type == "fast":
        return LLMFactory.get_fast_llm()
    elif type == "local":
        return LLMFactory.get_local_llm()
    return LLMFactory.get_local_llm()