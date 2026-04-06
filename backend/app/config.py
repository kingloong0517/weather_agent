from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Weather Agent"
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    # LLM 配置
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.7

    class Config:
        env_file = ".env"


settings = Settings()
