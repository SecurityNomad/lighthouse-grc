from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://lighthouse:changeme@localhost:5432/lighthouse"
    secret_key: str = "change-me"
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    environment: str = "development"
    upload_dir: str = "/app/uploads"
    seed_demo_data: bool = False
    # Evidence upload limits
    max_upload_mb: int = 25

    # ---- Phase 3 plugins (all optional; each runs in live or demo mode) ----
    # AWS Config / Security Hub — imports compliance findings as risks.
    aws_plugin_enabled: bool = True
    aws_region: str = "us-east-1"
    aws_demo_mode: bool = True          # use bundled sample findings (no boto3/creds)

    # MISP threat intelligence — imports events/attributes as risks.
    misp_plugin_enabled: bool = True
    misp_url: str = ""                  # e.g. https://misp.example.org
    misp_api_key: str = ""
    misp_verify_ssl: bool = True
    misp_demo_mode: bool = True         # use bundled sample events (no live MISP)

    # Slack — pushes notifications to an incoming-webhook URL.
    slack_plugin_enabled: bool = True
    slack_webhook_url: str = ""         # empty → demo mode (logs instead of posting)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
