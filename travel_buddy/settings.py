from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM Backend selection
    llm_backend: str = Field("ollama", env="LLM_BACKEND")

    
    # Ollama model
    ollama_model: str = Field("llama2", env="OLLAMA_MODEL")
    classification_model: str = Field("mistral", env="CLASSIFICATION_MODEL")

    # Generation params
    max_new_tokens: int = Field(256, env="MAX_NEW_TOKENS")
    temperature: float = Field(0.5, env="TEMPERATURE")
    top_p: float = Field(0.95, env="TOP_P")
    top_k: int = Field(50, env="TOP_K")

    # Runtime
    seed: Optional[int] = Field(None, env="SEED")
    
    # Memory and Conversation settings
    memory_storage_path: str = Field("memory_store.json", env="MEMORY_STORAGE_PATH")
    max_context_turns: int = Field(10, env="MAX_CONTEXT_TURNS")
    max_relevant_memories: int = Field(5, env="MAX_RELEVANT_MEMORIES")
    enable_memory: bool = Field(True, env="ENABLE_MEMORY")
    enable_conversation_mode: bool = Field(True, env="ENABLE_CONVERSATION_MODE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
