from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Weather Agent"
    debug: bool = True
    api_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"


settings = Settings()
