from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field
from langchain_groq import ChatGroq
from pydantic import SecretStr

class Settings(BaseSettings):
    GROQ_API_KEY: str = Field(default="")
    MODEL_FAST: str = "llama-3.1-8b-instant"
    MODEL_SMART: str = "llama-3.3-70b-versatile"
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
        """Zwraca model 'Mądry' (np. Llama-3-70b / GPT-4o) - Singleton"""
        settings = get_settings()
        
        return ChatGroq(
            model=settings.MODEL_SMART,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=temperature
        )

    @staticmethod
    @lru_cache(maxsize=1)
    def get_fast_llm(temperature: float = 0.0):
        """Zwraca model 'Szybki' (np. Llama-3-8b / GPT-3.5) - Singleton"""
        settings = get_settings()
        
        return ChatGroq(
            model=settings.MODEL_FAST,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=temperature
        )

def get_llm(type: str = "smart"):
    if type == "smart":
        return LLMFactory.get_smart_llm()
    return LLMFactory.get_fast_llm()