from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # HuggingFace transformers model
    hf_model_id: str = Field("distilgpt2", env="HF_MODEL_ID")
    hf_device: str = Field("cpu", env="HF_DEVICE")

    # Generation params
    max_new_tokens: int = Field(256, env="MAX_NEW_TOKENS")
    temperature: float = Field(0.5, env="TEMPERATURE")
    top_p: float = Field(0.95, env="TOP_P")
    top_k: float = Field(50, env="TOP_K")

    # Runtime
    seed: Optional[int] = Field(None, env="SEED")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
