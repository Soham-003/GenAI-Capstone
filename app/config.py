from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    chroma_path: str = "./data/chroma"
    docs_path: str = "./data/docs"
    prometheus_port: int = 8001

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
