from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openrouter_api_key: str = ""
    openai_api_key: str = ""        # legacy
    ollama_key: str = ""            # Ollama Cloud — used for interview chatbot
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    ai_provider: str = "openai"
    model_name: str = "openai/gpt-4o-mini"

    model_config = {"env_file": ".env"}

    @property
    def active_openrouter_key(self) -> str:
        return self.openrouter_api_key or self.openai_api_key

settings = Settings()
