from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(True, env="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field("travel-buddy", env="LANGCHAIN_PROJECT")
    langchain_api_key: str = Field("", env="LANGCHAIN_API_KEY")
    
    # LLM Backend selection
    llm_backend: str = Field("ollama", env="LLM_BACKEND")

    
    # Ollama model
    ollama_model: str = Field("hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M", env="OLLAMA_MODEL")
    classification_model: str = Field("hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M", env="CLASSIFICATION_MODEL")

    # Generation params
    max_new_tokens: int = Field(1024, env="MAX_NEW_TOKENS")
    temperature: float = Field(0.5, env="TEMPERATURE")
    top_p: float = Field(0.95, env="TOP_P")
    top_k: int = Field(50, env="TOP_K")
    max_ctx: int =  Field(32768, env="NUM_CTX")
    ollama_flash_attention: bool = Field(True, env="OLLAMA_FLASH_ATTENTION")

    # Runtime
    seed: Optional[int] = Field(None, env="SEED")
    
    # Memory and Conversation settings
    memory_storage_path: str = Field("memory_store.json", env="MEMORY_STORAGE_PATH")
    max_context_turns: int = Field(10, env="MAX_CONTEXT_TURNS")
    max_relevant_memories: int = Field(5, env="MAX_RELEVANT_MEMORIES")
    enable_memory: bool = Field(True, env="ENABLE_MEMORY")
    enable_conversation_mode: bool = Field(True, env="ENABLE_CONVERSATION_MODE")
    
    # API Configuration (disabled for now)
    weather_api_key: str = Field("", env="WEATHER_API_KEY")
    google_search_api_key: str = Field("", env="GOOGLE_SEARCH_API_KEY")
    google_search_engine_id: str = Field("", env="GOOGLE_SEARCH_ENGINE_ID")
    enable_weather_api: bool = Field(False, env="ENABLE_WEATHER_API")
    enable_web_search_api: bool = Field(False, env="ENABLE_WEB_SEARCH_API")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
