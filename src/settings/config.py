from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from pydantic import SecretStr
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router import SemanticRouter 

class Settings(BaseSettings):
    GROQ_API_KEY: str = Field(default="")
    MODEL_FAST: str = "llama-3.1-8b-instant"
    MODEL_SMART: str = "llama-3.3-70b-versatile"
    MODEL_LOCAL: str = "llama3.1"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_CHUNK_SIZE: int = 1000
    TEMPERATURE: float = 0.0
    CHUNK_SIZE: int = 10000 
    CHUNK_OVERLAP: int = 500
    PUBMED_API_KEY: str | None = None
    PUBMED_EMAIL: str = Field(default="unknown@example.com")
    class Config:
        env_file = ".env"
        
@lru_cache()
def get_settings() -> Settings:
    return Settings()

class LLMFactory:
    @staticmethod
    @lru_cache(maxsize=1)
    def get_smart_llm(temperature: float = 0.0):
        settings = get_settings()
        
        return ChatGroq(
            model=settings.MODEL_SMART,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=temperature
        )

    @staticmethod
    @lru_cache(maxsize=1)
    def get_fast_llm(temperature: float = 0.0):
        settings = get_settings()
        
        return ChatGroq(
            model=settings.MODEL_FAST,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=temperature
        )

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
    def get_encoder():
        """Zwraca encoder do semantic-router (HuggingFace/Local)"""
        settings = get_settings()
        return HuggingFaceEncoder(name=settings.EMBEDDING_MODEL)

    @staticmethod
    def get_semantic_router(routes: list):
        """Builds and returns a SemanticRouter instance (No caching here due to unhashable routes)"""
        sr = SemanticRouter(encoder=LLMFactory.get_encoder()) 
        if routes:
            sr.add(routes) 
        return sr

def get_llm(type: str = "local"):
    if type == "smart":
        return LLMFactory.get_smart_llm()
    elif type == "fast":
        return LLMFactory.get_fast_llm()
    elif type == "local":
        return LLMFactory.get_local_llm()
    return LLMFactory.get_local_llm()