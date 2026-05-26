from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://lighthouse:changeme@localhost:5432/lighthouse"
    secret_key: str = "change-me"
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    environment: str = "development"
    upload_dir: str = "/app/uploads"
    seed_demo_data: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
