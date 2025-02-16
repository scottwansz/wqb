# config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_title: str = "My FastAPI App"
    api_version: str = "1.0.0"
    api_description: str = "This is a sample FastAPI application."
    database_url: str = "sqlite:///./test.db"
    secret_key: str = "your_secret_key"
    api_username: str = "your_username"
    api_password: str = "your_password"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
