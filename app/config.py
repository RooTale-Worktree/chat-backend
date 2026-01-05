import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache

load_dotenv()


class Settings(BaseSettings):
    openai_api_key: str = Field(os.environ.get("OPENAI_API_KEY", ""), description="OpenAI API Key")
    model_name: str = Field("gpt-5.1-chat-latest", description="Language model name")
    temperature: float = Field(1.0, description="Sampling temperature for response generation")
    max_completion_tokens: int = Field(4096, description="Maximum tokens for completion")
    top_p: float = Field(1.0, description="Top-p sampling parameter")


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

__all__ = ["settings", "get_settings", "Settings"]
