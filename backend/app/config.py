from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://lighthouse:changeme@localhost:5432/lighthouse"

    @field_validator("database_url")
    @classmethod
    def _use_async_driver(cls, v: str) -> str:
        """Normalise the DATABASE_URL to the asyncpg driver.

        `fly postgres attach` (and Heroku-style providers generally) set
        DATABASE_URL to `postgres://…`, which SQLAlchemy's async engine cannot
        use — it resolves the default psycopg2 driver and fails at startup with
        an unhelpful "greenlet_spawn has not been called". Rewriting the scheme
        here means the deployment can use the provider's value unedited.
        """
        for prefix in ("postgres://", "postgresql://"):
            if v.startswith(prefix):
                return "postgresql+asyncpg://" + v[len(prefix):]
        return v
    secret_key: str = "change-me"
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    environment: str = "development"
    upload_dir: str = "/app/uploads"
    seed_demo_data: bool = False
    # Compiled SPA location. Populated by the multi-stage production image; the
    # path does not exist in local development, where Vite serves the frontend.
    static_dir: str = "/app/static"
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
